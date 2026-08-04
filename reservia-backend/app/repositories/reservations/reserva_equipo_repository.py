from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.reservations.reserva_equipo import ReservaEquipo
from app.models.reservations.reserva_sala import EstadoReserva


def create(
    db: DBSession,
    equipo_id: int,
    user_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str,
) -> ReservaEquipo:
    reserva = ReservaEquipo(
        equipo_id=equipo_id,
        user_id=user_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=motivo,
        estado=EstadoReserva.pendiente,
    )
    db.add(reserva)
    db.flush()
    return reserva


def confirm(db: DBSession, reserva: ReservaEquipo) -> ReservaEquipo:
    reserva.estado = EstadoReserva.confirmada
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def get_by_id(db: DBSession, id: int) -> Optional[ReservaEquipo]:
    return db.query(ReservaEquipo).filter(ReservaEquipo.id == id).first()


def list_confirmadas_by_equipo_fecha(
    db: DBSession, equipo_id: int, fecha: date
) -> list[ReservaEquipo]:
    return (
        db.query(ReservaEquipo)
        .filter(
            ReservaEquipo.equipo_id == equipo_id,
            ReservaEquipo.fecha == fecha,
            ReservaEquipo.estado == EstadoReserva.confirmada,
        )
        .all()
    )


def list_by_user(db: DBSession, user_id: int) -> list[ReservaEquipo]:
    return db.query(ReservaEquipo).filter(ReservaEquipo.user_id == user_id).all()


def cancel(
    db: DBSession, reserva: ReservaEquipo, cancelled_by_user_id: int
) -> ReservaEquipo:
    reserva.estado = EstadoReserva.cancelada
    reserva.cancelled_at = datetime.utcnow()
    reserva.cancelled_by_user_id = cancelled_by_user_id
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva