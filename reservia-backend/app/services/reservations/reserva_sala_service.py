import math
from datetime import date, datetime

from app.core import config
from app.models.auth.user import User, UserRole
from app.models.reservations.reserva_sala import EstadoReserva, ReservaSala
from app.models.resources.sala import SalaEstado
from app.repositories.reservations import reserva_sala_repository
from app.repositories.resources import sala_repository
from app.repositories.shared import audit_repository
from app.schemas.reservations.reserva import BookingCreateRequest
from app.services.notifications import notification_service
from app.services.reservations.availability_service import (
    add_minutes,
    generate_slots,
    is_aligned,
    mark_availability,
)


class SalaNotFoundError(Exception):
    pass


class SalaInactiveError(Exception):
    pass


class InvalidDateError(Exception):
    pass


class OutOfHoursError(Exception):
    pass


class MisalignedTimeError(Exception):
    pass


class OverlapError(Exception):
    pass


class ReservaNotFoundError(Exception):
    pass


class NotOwnerOrAdminError(Exception):
    pass


class CannotRescheduleError(Exception):
    pass


def _parse_operating_window():
    window_start = datetime.strptime(config.RESOURCE_OPERATING_START_TIME, "%H:%M").time()
    window_end = datetime.strptime(config.RESOURCE_OPERATING_END_TIME, "%H:%M").time()
    return window_start, window_end


def _blocks_overlap(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


def get_availability(db, sala_id: int, fecha: date) -> list[dict]:
    sala = sala_repository.get_by_id(db, sala_id)
    if sala is None:
        raise SalaNotFoundError("sala no encontrada")

    window_start, window_end = _parse_operating_window()
    slots = generate_slots(window_start, window_end, config.RESOURCE_SLOT_DURATION_MINUTES)

    existentes = reserva_sala_repository.list_confirmadas_by_sala_fecha(db, sala_id, fecha)
    booked_ranges = [(r.hora_inicio, r.hora_fin) for r in existentes]

    return mark_availability(slots, booked_ranges)


def create_reserva(db, sala_id: int, user_id: int, data: BookingCreateRequest) -> ReservaSala:
    sala = sala_repository.get_by_id_for_update(db, sala_id)
    if sala is None:
        raise SalaNotFoundError("sala no encontrada")

    if sala.estado == SalaEstado.inactive:
        raise SalaInactiveError("la sala esta inactiva")

    if data.fecha < date.today():
        raise InvalidDateError("la fecha no puede ser anterior a hoy")

    window_start, window_end = _parse_operating_window()

    if not is_aligned(data.hora_inicio, window_start, config.RESOURCE_SLOT_DURATION_MINUTES):
        raise MisalignedTimeError(
            "la hora de inicio no esta alineada con los bloques disponibles"
        )

    hora_fin = add_minutes(
        data.hora_inicio, data.num_bloques * config.RESOURCE_SLOT_DURATION_MINUTES
    )

    if data.hora_inicio < window_start or hora_fin > window_end:
        raise OutOfHoursError("el horario solicitado esta fuera del horario de operacion")

    existentes = reserva_sala_repository.list_confirmadas_by_sala_fecha(
        db, sala_id, data.fecha
    )
    for existente in existentes:
        if _blocks_overlap(
            existente.hora_inicio, existente.hora_fin, data.hora_inicio, hora_fin
        ):
            raise OverlapError("el horario solicitado se solapa con una reserva existente")

    reserva = reserva_sala_repository.create(
        db,
        sala_id=sala_id,
        user_id=user_id,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=hora_fin,
        motivo=data.motivo,
    )
    reserva = reserva_sala_repository.confirm(db, reserva)

    audit_repository.log_action(
        db,
        actor_user_id=user_id,
        action="reserva_sala.created",
        entity_type="reserva_sala",
        entity_id=reserva.id,
        metadata=None,
    )

    notification_service.create_notification(
        db,
        user_id=user_id,
        tipo="reserva_confirmada",
        mensaje=f"Tu reserva de '{sala.nombre}' para el {data.fecha} a las "
                f"{data.hora_inicio.strftime('%H:%M')} fue confirmada.",
        entity_type="reserva_sala",
        entity_id=reserva.id,
    )

    return reserva


def list_my_reservas(db, user_id: int, page: int, page_size: int) -> dict:
    items, total = reserva_sala_repository.list_by_user_paginated(db, user_id, page, page_size)
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def list_all_reservas(db, page: int, page_size: int) -> dict:
    rows, total = reserva_sala_repository.list_all_with_details_paginated(db, page, page_size)
    items = [
        {
            "id": reserva.id, "sala_id": reserva.sala_id, "sala_nombre": sala_nombre,
            "user_id": reserva.user_id, "user_full_name": user_full_name, "user_email": user_email,
            "fecha": reserva.fecha, "hora_inicio": reserva.hora_inicio, "hora_fin": reserva.hora_fin,
            "motivo": reserva.motivo, "estado": reserva.estado,
        }
        for reserva, sala_nombre, user_full_name, user_email in rows
    ]
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def cancel_reserva(db, reserva_id: int, actor_user: User) -> ReservaSala:
    reserva = reserva_sala_repository.get_by_id(db, reserva_id)
    if reserva is None:
        raise ReservaNotFoundError("reserva no encontrada")

    if actor_user.role != UserRole.admin and reserva.user_id != actor_user.id:
        raise NotOwnerOrAdminError("no tienes permiso para cancelar esta reserva")

    if reserva.estado == EstadoReserva.cancelada:
        return reserva

    reserva = reserva_sala_repository.cancel(
        db, reserva, cancelled_by_user_id=actor_user.id
    )

    audit_repository.log_action(
        db,
        actor_user_id=actor_user.id,
        action="reserva_sala.cancelled",
        entity_type="reserva_sala",
        entity_id=reserva.id,
        metadata=None,
    )

    return reserva


def reschedule_reserva(db, reserva_id: int, actor_user, data: BookingCreateRequest):
    reserva = reserva_sala_repository.get_by_id(db, reserva_id)
    if reserva is None:
        raise ReservaNotFoundError("reserva no encontrada")

    if actor_user.role.value != "admin" and reserva.user_id != actor_user.id:
        raise NotOwnerOrAdminError("no tienes permiso sobre esta reserva")

    if reserva.estado.value != "confirmada":
        raise CannotRescheduleError("solo se pueden reprogramar reservas confirmadas")

    original_user_id = reserva.user_id
    sala_id = reserva.sala_id

    reserva_sala_repository.cancel(db, reserva, cancelled_by_user_id=actor_user.id)

    nueva = create_reserva(db, sala_id, original_user_id, data)

    audit_repository.log_action(
        db, actor_user_id=actor_user.id, action="reserva_sala.rescheduled",
        entity_type="reserva_sala", entity_id=nueva.id,
        metadata={"old_reserva_id": reserva_id},
    )

    return nueva