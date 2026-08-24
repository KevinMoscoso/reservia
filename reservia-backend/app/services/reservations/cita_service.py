import math
from datetime import date, datetime

from app.core import config
from app.models.auth.user import User, UserRole
from app.models.reservations.cita import Cita
from app.models.reservations.reserva_sala import EstadoReserva
from app.repositories.auth import user_repository
from app.repositories.providers import provider_repository
from app.repositories.reservations import cita_repository
from app.repositories.shared import audit_repository
from app.schemas.reservations.reserva import BookingCreateRequest
from app.services.notifications import notification_service
from app.services.reservations.availability_service import (
    add_minutes,
    generate_slots,
    is_aligned,
    mark_availability,
)

DAY_OF_WEEK_BY_INDEX = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class ProviderProfileNotFoundError(Exception):
    pass


class InvalidDateError(Exception):
    pass


class OutOfScheduleError(Exception):
    pass


class MisalignedTimeError(Exception):
    pass


class OverlapError(Exception):
    pass


class CitaNotFoundError(Exception):
    pass


class NotOwnerOrProviderError(Exception):
    pass


def _blocks_overlap(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


def get_availability(db, provider_profile_id: int, fecha: date) -> list[dict]:
    profile = provider_repository.get_profile_by_id(db, provider_profile_id)
    if profile is None:
        raise ProviderProfileNotFoundError("perfil de proveedor no encontrado")

    day_key = DAY_OF_WEEK_BY_INDEX[fecha.weekday()]
    blocks = provider_repository.list_schedule_by_profile(
        db, provider_profile_id, only_active=True
    )
    day_blocks = [b for b in blocks if b.day_of_week.value == day_key]

    existentes = cita_repository.list_confirmadas_by_provider_fecha(
        db, provider_profile_id, fecha
    )
    booked_ranges = [(c.hora_inicio, c.hora_fin) for c in existentes]

    availability: list[dict] = []
    for block in day_blocks:
        slots = generate_slots(block.start_time, block.end_time, profile.slot_duration_minutes)
        availability.extend(mark_availability(slots, booked_ranges))

    return availability


def create_cita(
    db, provider_profile_id: int, user_id: int, data: BookingCreateRequest
) -> Cita:
    profile = provider_repository.get_profile_by_id_for_update(db, provider_profile_id)
    if profile is None:
        raise ProviderProfileNotFoundError("perfil de proveedor no encontrado")

    if data.fecha < date.today():
        raise InvalidDateError("la fecha no puede ser anterior a hoy")

    day_key = DAY_OF_WEEK_BY_INDEX[data.fecha.weekday()]
    blocks = provider_repository.list_schedule_by_profile(
        db, provider_profile_id, only_active=True
    )
    day_blocks = [b for b in blocks if b.day_of_week.value == day_key]

    hora_fin = add_minutes(
        data.hora_inicio, data.num_bloques * profile.slot_duration_minutes
    )

    matching_block = None
    for block in day_blocks:
        if block.start_time <= data.hora_inicio and hora_fin <= block.end_time:
            matching_block = block
            break

    if matching_block is None:
        raise OutOfScheduleError(
            "el horario solicitado no corresponde a un bloque de disponibilidad del proveedor"
        )

    if not is_aligned(
        data.hora_inicio, matching_block.start_time, profile.slot_duration_minutes
    ):
        raise MisalignedTimeError(
            "la hora de inicio no esta alineada con los bloques de este horario"
        )

    existentes = cita_repository.list_confirmadas_by_provider_fecha(
        db, provider_profile_id, data.fecha
    )
    for existente in existentes:
        if _blocks_overlap(
            existente.hora_inicio, existente.hora_fin, data.hora_inicio, hora_fin
        ):
            raise OverlapError("el horario solicitado se solapa con una cita existente")

    cita = cita_repository.create(
        db,
        provider_profile_id=provider_profile_id,
        user_id=user_id,
        fecha=data.fecha,
        hora_inicio=data.hora_inicio,
        hora_fin=hora_fin,
        motivo=data.motivo,
    )
    cita = cita_repository.confirm(db, cita)

    audit_repository.log_action(
        db,
        actor_user_id=user_id,
        action="cita.created",
        entity_type="cita",
        entity_id=cita.id,
        metadata=None,
    )

    provider_user = user_repository.get_by_id(db, profile.user_id)
    client_user = user_repository.get_by_id(db, user_id)

    notification_service.create_notification(
        db, user_id=user_id, tipo="cita_confirmada",
        mensaje=f"Tu cita con {provider_user.full_name} el {data.fecha} a las "
                f"{data.hora_inicio.strftime('%H:%M')} fue confirmada.",
        entity_type="cita", entity_id=cita.id,
    )
    notification_service.create_notification(
        db, user_id=profile.user_id, tipo="cita_confirmada",
        mensaje=f"Nueva cita agendada por {client_user.full_name} el {data.fecha} "
                f"a las {data.hora_inicio.strftime('%H:%M')}.",
        entity_type="cita", entity_id=cita.id,
    )

    return cita


def list_my_citas(db, user_id: int, page: int, page_size: int) -> dict:
    items, total = cita_repository.list_by_user_paginated(db, user_id, page, page_size)
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def list_all_reservas(db, page: int, page_size: int) -> dict:
    rows, total = cita_repository.list_all_with_details_paginated(db, page, page_size)
    items = [
        {
            "id": cita.id, "provider_profile_id": cita.provider_profile_id,
            "provider_full_name": provider_full_name,
            "user_id": cita.user_id, "user_full_name": client_full_name, "user_email": client_email,
            "fecha": cita.fecha, "hora_inicio": cita.hora_inicio, "hora_fin": cita.hora_fin,
            "motivo": cita.motivo, "estado": cita.estado,
        }
        for cita, provider_full_name, client_full_name, client_email in rows
    ]
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def cancel_cita(db, cita_id: int, actor_user: User) -> Cita:
    cita = cita_repository.get_by_id(db, cita_id)
    if cita is None:
        raise CitaNotFoundError("cita no encontrada")

    is_owner = actor_user.id == cita.user_id
    is_provider_owner = (
        actor_user.role == UserRole.provider
        and cita.provider_profile is not None
        and actor_user.id == cita.provider_profile.user_id
    )

    if not (is_owner or is_provider_owner):
        raise NotOwnerOrProviderError("no tienes permiso para cancelar esta cita")

    if cita.estado == EstadoReserva.cancelada:
        return cita

    cita = cita_repository.cancel(db, cita, cancelled_by_user_id=actor_user.id)

    audit_repository.log_action(
        db,
        actor_user_id=actor_user.id,
        action="cita.cancelled",
        entity_type="cita",
        entity_id=cita.id,
        metadata=None,
    )

    return cita