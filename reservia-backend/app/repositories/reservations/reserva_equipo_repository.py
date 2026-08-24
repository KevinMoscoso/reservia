from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.auth.user import User
from app.models.reservations.reserva_equipo import ReservaEquipo
from app.models.reservations.reserva_sala import EstadoReserva
from app.models.resources.equipo import Equipo


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


def list_by_user_paginated(db: DBSession, user_id: int, page: int, page_size: int):
    query = (
        db.query(ReservaEquipo)
        .filter(ReservaEquipo.user_id == user_id)
        .order_by(ReservaEquipo.fecha.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def list_all_with_details_paginated(db: DBSession, page: int, page_size: int):
    base_query = (
        db.query(ReservaEquipo, Equipo.nombre, User.full_name, User.email)
        .join(Equipo, ReservaEquipo.equipo_id == Equipo.id)
        .join(User, ReservaEquipo.user_id == User.id)
        .order_by(ReservaEquipo.fecha.desc())
    )
    total = base_query.count()
    items = base_query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def list_confirmadas_by_fecha_range(
    db: DBSession, fecha_inicio: date, fecha_fin: date
) -> list[ReservaEquipo]:
    return db.query(ReservaEquipo).filter(
        ReservaEquipo.estado == EstadoReserva.confirmada,
        ReservaEquipo.fecha >= fecha_inicio,
        ReservaEquipo.fecha <= fecha_fin,
    ).all()


def list_created_in_range(
    db: DBSession, start_dt: datetime, end_dt: datetime
) -> list[ReservaEquipo]:
    return db.query(ReservaEquipo).filter(
        ReservaEquipo.created_at >= start_dt,
        ReservaEquipo.created_at < end_dt,
    ).all()


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