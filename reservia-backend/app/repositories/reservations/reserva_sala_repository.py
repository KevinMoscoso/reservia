from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.auth.user import User
from app.models.reservations.reserva_sala import EstadoReserva, ReservaSala
from app.models.resources.sala import Sala


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


def list_all_with_details(db: DBSession) -> list[tuple[ReservaSala, str, str, str]]:
    """
    Retorna tuplas (reserva, sala_nombre, user_full_name, user_email),
    ordenadas por fecha descendente.
    """
    results = (
        db.query(ReservaSala, Sala.nombre, User.full_name, User.email)
        .join(Sala, ReservaSala.sala_id == Sala.id)
        .join(User, ReservaSala.user_id == User.id)
        .order_by(ReservaSala.fecha.desc())
        .all()
    )
    return results


def list_confirmadas_by_fecha_range(
    db: DBSession, fecha_inicio: date, fecha_fin: date
) -> list[ReservaSala]:
    return db.query(ReservaSala).filter(
        ReservaSala.estado == EstadoReserva.confirmada,
        ReservaSala.fecha >= fecha_inicio,
        ReservaSala.fecha <= fecha_fin,
    ).all()


def list_created_in_range(
    db: DBSession, start_dt: datetime, end_dt: datetime
) -> list[ReservaSala]:
    return db.query(ReservaSala).filter(
        ReservaSala.created_at >= start_dt,
        ReservaSala.created_at < end_dt,
    ).all()


def cancel(db: DBSession, reserva: ReservaSala, cancelled_by_user_id: int) -> ReservaSala:
    reserva.estado = EstadoReserva.cancelada
    reserva.cancelled_at = datetime.utcnow()
    reserva.cancelled_by_user_id = cancelled_by_user_id
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva