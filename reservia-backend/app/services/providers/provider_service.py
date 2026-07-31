from datetime import time

from app.models.auth.user import User
from app.models.providers.provider_profile import ProviderProfile
from app.models.providers.provider_schedule import ProviderSchedule, ScheduleEstado
from app.repositories.providers import provider_repository
from app.repositories.shared import audit_repository
from app.schemas.providers.provider import (
    ProviderProfileUpdateRequest,
    ScheduleBlockCreateRequest,
)


class ProviderProfileNotFoundError(Exception):
    pass


class ScheduleOverlapError(Exception):
    pass


class ScheduleBlockNotFoundError(Exception):
    pass


class NotScheduleOwnerError(Exception):
    pass


def ensure_provider_profile(
    db, user_id: int, default_slot_duration_minutes: int = 30
) -> ProviderProfile:
    profile = provider_repository.get_profile_by_user_id(db, user_id)
    if profile is not None:
        return profile

    return provider_repository.create_profile(
        db, user_id=user_id, slot_duration_minutes=default_slot_duration_minutes
    )


def get_own_profile(db, user: User) -> ProviderProfile:
    profile = provider_repository.get_profile_by_user_id(db, user.id)
    if profile is None:
        profile = ensure_provider_profile(db, user_id=user.id)
    return profile


def update_own_profile(
    db, user: User, data: ProviderProfileUpdateRequest
) -> ProviderProfile:
    profile = get_own_profile(db, user)
    profile = provider_repository.update_profile(
        db, profile, slot_duration_minutes=data.slot_duration_minutes
    )

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="provider.profile_updated",
        entity_type="provider_profile",
        entity_id=profile.id,
        metadata=None,
    )

    return profile


def list_public_providers(db):
    return provider_repository.list_active_providers(db)


def get_public_schedule(db, provider_profile_id: int) -> list[ProviderSchedule]:
    profile = provider_repository.get_profile_by_id(db, provider_profile_id)
    if profile is None:
        raise ProviderProfileNotFoundError("perfil de proveedor no encontrado")

    return provider_repository.list_schedule_by_profile(
        db, provider_profile_id, only_active=True
    )


def list_own_schedule(db, user: User) -> list[ProviderSchedule]:
    profile = get_own_profile(db, user)
    return provider_repository.list_schedule_by_profile(
        db, profile.id, only_active=False
    )


def _blocks_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a


def add_schedule_block(
    db, user: User, data: ScheduleBlockCreateRequest
) -> ProviderSchedule:
    profile = get_own_profile(db, user)

    existing_blocks = provider_repository.list_schedule_by_profile(
        db, profile.id, only_active=True
    )

    for block in existing_blocks:
        if block.day_of_week.value == data.day_of_week and _blocks_overlap(
            block.start_time, block.end_time, data.start_time, data.end_time
        ):
            raise ScheduleOverlapError("el bloque se solapa con uno existente")

    block = provider_repository.create_schedule_block(
        db,
        provider_profile_id=profile.id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
    )

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="provider.schedule_created",
        entity_type="provider_schedule",
        entity_id=block.id,
        metadata=None,
    )

    return block


def deactivate_own_schedule_block(db, user: User, block_id: int) -> ProviderSchedule:
    block = provider_repository.get_schedule_block_by_id(db, block_id)
    if block is None:
        raise ScheduleBlockNotFoundError("bloque de horario no encontrado")

    if block.provider_profile.user_id != user.id:
        raise NotScheduleOwnerError("no eres el propietario de este bloque")

    if block.estado == ScheduleEstado.inactive:
        return block

    block = provider_repository.deactivate_schedule_block(db, block)

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="provider.schedule_deactivated",
        entity_type="provider_schedule",
        entity_id=block.id,
        metadata=None,
    )

    return block