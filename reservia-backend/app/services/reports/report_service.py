import csv
import io
from datetime import date, datetime, time, timedelta

from app.core import config
from app.models.auth.user import UserRole
from app.models.reservations.reserva_sala import EstadoReserva
from app.repositories.providers import provider_repository
from app.repositories.reservations import cita_repository, reserva_equipo_repository, reserva_sala_repository
from app.repositories.resources import equipo_repository, sala_repository
from app.services.reservations.availability_service import generate_slots


def _parse_operating_window():
    window_start = datetime.strptime(config.RESOURCE_OPERATING_START_TIME, "%H:%M").time()
    window_end = datetime.strptime(config.RESOURCE_OPERATING_END_TIME, "%H:%M").time()
    return window_start, window_end


def _slots_per_day() -> int:
    window_start, window_end = _parse_operating_window()
    return len(generate_slots(window_start, window_end, config.RESOURCE_SLOT_DURATION_MINUTES))


def _bloques_from_range(hora_inicio: time, hora_fin: time) -> int:
    start_dt = datetime.combine(date.today(), hora_inicio)
    end_dt = datetime.combine(date.today(), hora_fin)
    minutos = (end_dt - start_dt).total_seconds() / 60
    return int(minutos // config.RESOURCE_SLOT_DURATION_MINUTES)


def get_occupancy_report(db, fecha_inicio: date, fecha_fin: date) -> dict:
    dias = (fecha_fin - fecha_inicio).days + 1
    bloques_disponibles_por_recurso = _slots_per_day() * dias

    salas = sala_repository.list_all(db)
    equipos = equipo_repository.list_all(db)

    reservas_salas = reserva_sala_repository.list_confirmadas_by_fecha_range(db, fecha_inicio, fecha_fin)
    reservas_equipos = reserva_equipo_repository.list_confirmadas_by_fecha_range(db, fecha_inicio, fecha_fin)

    bloques_por_sala, conteo_por_sala = {}, {}
    for r in reservas_salas:
        bloques_por_sala[r.sala_id] = bloques_por_sala.get(r.sala_id, 0) + _bloques_from_range(r.hora_inicio, r.hora_fin)
        conteo_por_sala[r.sala_id] = conteo_por_sala.get(r.sala_id, 0) + 1

    bloques_por_equipo, conteo_por_equipo = {}, {}
    for r in reservas_equipos:
        bloques_por_equipo[r.equipo_id] = bloques_por_equipo.get(r.equipo_id, 0) + _bloques_from_range(r.hora_inicio, r.hora_fin)
        conteo_por_equipo[r.equipo_id] = conteo_por_equipo.get(r.equipo_id, 0) + 1

    items = []
    for sala in salas:
        bloques_reservados = bloques_por_sala.get(sala.id, 0)
        porcentaje = round((bloques_reservados / bloques_disponibles_por_recurso) * 100, 2) if bloques_disponibles_por_recurso else 0.0
        items.append({
            "resource_type": "sala", "resource_id": sala.id, "resource_nombre": sala.nombre,
            "reservas_confirmadas": conteo_por_sala.get(sala.id, 0),
            "bloques_reservados": bloques_reservados,
            "bloques_disponibles": bloques_disponibles_por_recurso,
            "porcentaje_ocupacion": porcentaje,
        })
    for equipo in equipos:
        bloques_reservados = bloques_por_equipo.get(equipo.id, 0)
        porcentaje = round((bloques_reservados / bloques_disponibles_por_recurso) * 100, 2) if bloques_disponibles_por_recurso else 0.0
        items.append({
            "resource_type": "equipo", "resource_id": equipo.id, "resource_nombre": equipo.nombre,
            "reservas_confirmadas": conteo_por_equipo.get(equipo.id, 0),
            "bloques_reservados": bloques_reservados,
            "bloques_disponibles": bloques_disponibles_por_recurso,
            "porcentaje_ocupacion": porcentaje,
        })

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "items": items}


def occupancy_report_to_csv(report: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tipo", "Nombre", "Reservas confirmadas", "Bloques reservados", "Bloques disponibles", "% Ocupacion"])
    for item in report["items"]:
        writer.writerow([item["resource_type"], item["resource_nombre"], item["reservas_confirmadas"],
                          item["bloques_reservados"], item["bloques_disponibles"], item["porcentaje_ocupacion"]])
    return output.getvalue()


def get_provider_activity_report(db, fecha_inicio: date, fecha_fin: date, current_user) -> dict:
    if current_user.role == UserRole.provider:
        profile = provider_repository.get_profile_by_user_id(db, current_user.id)
        provider_profiles = [(profile, current_user)] if profile else []
    else:
        provider_profiles = provider_repository.list_active_providers(db)

    items = []
    for profile, user in provider_profiles:
        citas = cita_repository.list_by_fecha_range(db, fecha_inicio, fecha_fin, provider_profile_id=profile.id)
        confirmadas = sum(1 for c in citas if c.estado == EstadoReserva.confirmada)
        canceladas = sum(1 for c in citas if c.estado == EstadoReserva.cancelada)
        items.append({
            "provider_profile_id": profile.id, "provider_full_name": user.full_name,
            "citas_confirmadas": confirmadas, "citas_canceladas": canceladas,
            "total_citas": confirmadas + canceladas,
        })

    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "items": items}


def provider_activity_report_to_csv(report: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Proveedor", "Citas confirmadas", "Citas canceladas", "Total"])
    for item in report["items"]:
        writer.writerow([item["provider_full_name"], item["citas_confirmadas"], item["citas_canceladas"], item["total_citas"]])
    return output.getvalue()


def get_system_activity_report(db, fecha_inicio: date, fecha_fin: date) -> dict:
    start_dt = datetime.combine(fecha_inicio, time.min)
    end_dt = datetime.combine(fecha_fin + timedelta(days=1), time.min)

    reservas_salas = reserva_sala_repository.list_created_in_range(db, start_dt, end_dt)
    reservas_equipos = reserva_equipo_repository.list_created_in_range(db, start_dt, end_dt)
    citas = cita_repository.list_created_in_range(db, start_dt, end_dt)

    usuarios = set()
    cancelaciones = 0
    for r in reservas_salas:
        usuarios.add(r.user_id)
        if r.estado == EstadoReserva.cancelada:
            cancelaciones += 1
    for r in reservas_equipos:
        usuarios.add(r.user_id)
        if r.estado == EstadoReserva.cancelada:
            cancelaciones += 1
    for c in citas:
        usuarios.add(c.user_id)
        if c.estado == EstadoReserva.cancelada:
            cancelaciones += 1

    total_general = len(reservas_salas) + len(reservas_equipos) + len(citas)
    porcentaje_cancelacion = round((cancelaciones / total_general) * 100, 2) if total_general else 0.0

    return {
        "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin,
        "usuarios_activos": len(usuarios),
        "total_reservas_salas": len(reservas_salas),
        "total_reservas_equipos": len(reservas_equipos),
        "total_citas": len(citas),
        "total_general": total_general,
        "total_cancelaciones": cancelaciones,
        "porcentaje_cancelacion": porcentaje_cancelacion,
    }


def system_activity_report_to_csv(report: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Usuarios activos", "Total reservas salas", "Total reservas equipos",
                      "Total citas", "Total general", "Total cancelaciones", "% Cancelacion"])
    writer.writerow([report["usuarios_activos"], report["total_reservas_salas"], report["total_reservas_equipos"],
                      report["total_citas"], report["total_general"], report["total_cancelaciones"],
                      report["porcentaje_cancelacion"]])
    return output.getvalue()