from datetime import date, datetime, time
from typing import Optional

from sqlalchemy.orm import Session as DBSession, aliased

from app.models.auth.user import User
from app.models.providers.provider_profile import ProviderProfile
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


def list_all_with_details(db: DBSession) -> list[tuple[Cita, str, str, str]]:
    """
    Retorna tuplas (cita, provider_full_name, client_full_name, client_email).
    """
    ProviderUser = aliased(User)
    ClientUser = aliased(User)

    results = (
        db.query(Cita, ProviderUser.full_name, ClientUser.full_name, ClientUser.email)
        .join(ProviderProfile, Cita.provider_profile_id == ProviderProfile.id)
        .join(ProviderUser, ProviderProfile.user_id == ProviderUser.id)
        .join(ClientUser, Cita.user_id == ClientUser.id)
        .order_by(Cita.fecha.desc())
        .all()
    )
    return results


def list_by_fecha_range(
    db: DBSession, fecha_inicio: date, fecha_fin: date, provider_profile_id: int = None
) -> list[Cita]:
    query = db.query(Cita).filter(
        Cita.fecha >= fecha_inicio,
        Cita.fecha <= fecha_fin,
    )
    if provider_profile_id is not None:
        query = query.filter(Cita.provider_profile_id == provider_profile_id)
    return query.all()


def list_created_in_range(
    db: DBSession, start_dt: datetime, end_dt: datetime
) -> list[Cita]:
    return db.query(Cita).filter(
        Cita.created_at >= start_dt,
        Cita.created_at < end_dt,
    ).all()


def cancel(db: DBSession, cita: Cita, cancelled_by_user_id: int) -> Cita:
    cita.estado = EstadoReserva.cancelada
    cita.cancelled_at = datetime.utcnow()
    cita.cancelled_by_user_id = cancelled_by_user_id
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita