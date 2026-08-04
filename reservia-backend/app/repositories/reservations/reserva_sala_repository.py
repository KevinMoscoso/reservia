from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.reservations.reserva_sala import EstadoReserva, ReservaSala


def create(
    db: DBSession,
    sala_id: int,
    user_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str,
) -> ReservaSala:
    reserva = ReservaSala(
        sala_id=sala_id,
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


def confirm(db: DBSession, reserva: ReservaSala) -> ReservaSala:
    reserva.estado = EstadoReserva.confirmada
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def get_by_id(db: DBSession, id: int) -> Optional[ReservaSala]:
    return db.query(ReservaSala).filter(ReservaSala.id == id).first()


def list_confirmadas_by_sala_fecha(
    db: DBSession, sala_id: int, fecha: date
) -> list[ReservaSala]:
    return (
        db.query(ReservaSala)
        .filter(
            ReservaSala.sala_id == sala_id,
            ReservaSala.fecha == fecha,
            ReservaSala.estado == EstadoReserva.confirmada,
        )
        .all()
    )


def list_by_user(db: DBSession, user_id: int) -> list[ReservaSala]:
    return db.query(ReservaSala).filter(ReservaSala.user_id == user_id).all()


def cancel(db: DBSession, reserva: ReservaSala, cancelled_by_user_id: int) -> ReservaSala:
    reserva.estado = EstadoReserva.cancelada
    reserva.cancelled_at = datetime.utcnow()
    reserva.cancelled_by_user_id = cancelled_by_user_id
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva