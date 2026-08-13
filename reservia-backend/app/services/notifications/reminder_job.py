from datetime import datetime, timedelta

from app.core import config
from app.core.database import SessionLocal
from app.models.reservations.cita import Cita
from app.models.reservations.reserva_equipo import ReservaEquipo
from app.models.reservations.reserva_sala import EstadoReserva, ReservaSala
from app.services.notifications import notification_service


def check_and_send_reminders(session_factory=SessionLocal):
    db = session_factory()
    try:
        now = datetime.now()
        threshold = now + timedelta(hours=config.REMINDER_HOURS_BEFORE)

        # --- Reservas de salas ---
        pendientes = db.query(ReservaSala).filter(
            ReservaSala.estado == EstadoReserva.confirmada,
            ReservaSala.recordatorio_enviado == False,  # noqa: E712
        ).all()
        for r in pendientes:
            inicio = datetime.combine(r.fecha, r.hora_inicio)
            if now <= inicio <= threshold:
                notification_service.create_notification(
                    db, user_id=r.user_id, tipo="recordatorio",
                    mensaje=f"Recordatorio: tu reserva de sala del {r.fecha} a las "
                            f"{r.hora_inicio.strftime('%H:%M')} es en menos de "
                            f"{config.REMINDER_HOURS_BEFORE} hora(s).",
                    entity_type="reserva_sala", entity_id=r.id,
                )
                r.recordatorio_enviado = True
                db.add(r)
            elif inicio < now:
                r.recordatorio_enviado = True
                db.add(r)
        db.commit()

        # --- Reservas de equipos (mismo patron exacto, con ReservaEquipo) ---
        pendientes_equipos = db.query(ReservaEquipo).filter(
            ReservaEquipo.estado == EstadoReserva.confirmada,
            ReservaEquipo.recordatorio_enviado == False,  # noqa: E712
        ).all()
        for r in pendientes_equipos:
            inicio = datetime.combine(r.fecha, r.hora_inicio)
            if now <= inicio <= threshold:
                notification_service.create_notification(
                    db, user_id=r.user_id, tipo="recordatorio",
                    mensaje=f"Recordatorio: tu reserva de equipo del {r.fecha} a las "
                            f"{r.hora_inicio.strftime('%H:%M')} es en menos de "
                            f"{config.REMINDER_HOURS_BEFORE} hora(s).",
                    entity_type="reserva_equipo", entity_id=r.id,
                )
                r.recordatorio_enviado = True
                db.add(r)
            elif inicio < now:
                r.recordatorio_enviado = True
                db.add(r)
        db.commit()

        # --- Citas ---
        pendientes_citas = db.query(Cita).filter(
            Cita.estado == EstadoReserva.confirmada,
            Cita.recordatorio_enviado == False,  # noqa: E712
        ).all()
        for c in pendientes_citas:
            inicio = datetime.combine(c.fecha, c.hora_inicio)
            if now <= inicio <= threshold:
                mensaje_base = (
                    f"Recordatorio: cita del {c.fecha} a las "
                    f"{c.hora_inicio.strftime('%H:%M')} es en menos de "
                    f"{config.REMINDER_HOURS_BEFORE} hora(s)."
                )
                notification_service.create_notification(
                    db, user_id=c.user_id, tipo="recordatorio",
                    mensaje=mensaje_base, entity_type="cita", entity_id=c.id,
                )
                notification_service.create_notification(
                    db, user_id=c.provider_profile.user_id, tipo="recordatorio",
                    mensaje=mensaje_base, entity_type="cita", entity_id=c.id,
                )
                c.recordatorio_enviado = True
                db.add(c)
            elif inicio < now:
                c.recordatorio_enviado = True
                db.add(c)
        db.commit()
    finally:
        db.close()