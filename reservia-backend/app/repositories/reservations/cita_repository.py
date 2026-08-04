from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.reservations.cita import Cita
from app.models.reservations.reserva_sala import EstadoReserva


def create(
    db: DBSession,
    provider_profile_id: int,
    user_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    motivo: str,
) -> Cita:
    cita = Cita(
        provider_profile_id=provider_profile_id,
        user_id=user_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=motivo,
        estado=EstadoReserva.pendiente,
    )
    db.add(cita)
    db.flush()
    return cita


def confirm(db: DBSession, cita: Cita) -> Cita:
    cita.estado = EstadoReserva.confirmada
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita


def get_by_id(db: DBSession, id: int) -> Optional[Cita]:
    return db.query(Cita).filter(Cita.id == id).first()


def list_confirmadas_by_provider_fecha(
    db: DBSession, provider_profile_id: int, fecha: date
) -> list[Cita]:
    return (
        db.query(Cita)
        .filter(
            Cita.provider_profile_id == provider_profile_id,
            Cita.fecha == fecha,
            Cita.estado == EstadoReserva.confirmada,
        )
        .all()
    )


def list_by_user(db: DBSession, user_id: int) -> list[Cita]:
    return db.query(Cita).filter(Cita.user_id == user_id).all()


def cancel(db: DBSession, cita: Cita, cancelled_by_user_id: int) -> Cita:
    cita.estado = EstadoReserva.cancelada
    cita.cancelled_at = datetime.utcnow()
    cita.cancelled_by_user_id = cancelled_by_user_id
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita