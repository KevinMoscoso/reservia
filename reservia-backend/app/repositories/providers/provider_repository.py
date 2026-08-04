from datetime import time
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.auth.user import User, UserRole, UserStatus
from app.models.providers.provider_profile import ProviderProfile
from app.models.providers.provider_schedule import ProviderSchedule, ScheduleEstado


def get_profile_by_user_id(db: DBSession, user_id: int) -> Optional[ProviderProfile]:
    return (
        db.query(ProviderProfile)
        .filter(ProviderProfile.user_id == user_id)
        .first()
    )


def get_profile_by_id(db: DBSession, id: int) -> Optional[ProviderProfile]:
    return db.query(ProviderProfile).filter(ProviderProfile.id == id).first()


def get_profile_by_id_for_update(db: DBSession, id: int) -> Optional[ProviderProfile]:
    return (
        db.query(ProviderProfile)
        .filter(ProviderProfile.id == id)
        .with_for_update()
        .first()
    )


def create_profile(
    db: DBSession, user_id: int, slot_duration_minutes: int = 30
) -> ProviderProfile:
    profile = ProviderProfile(
        user_id=user_id, slot_duration_minutes=slot_duration_minutes
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: DBSession, profile: ProviderProfile, slot_duration_minutes: int
) -> ProviderProfile:
    profile.slot_duration_minutes = slot_duration_minutes
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_active_providers(db: DBSession) -> list[tuple[ProviderProfile, User]]:
    return (
        db.query(ProviderProfile, User)
        .join(User, ProviderProfile.user_id == User.id)
        .filter(User.role == UserRole.provider, User.status == UserStatus.active)
        .all()
    )


def create_schedule_block(
    db: DBSession,
    provider_profile_id: int,
    day_of_week: str,
    start_time: time,
    end_time: time,
) -> ProviderSchedule:
    block = ProviderSchedule(
        provider_profile_id=provider_profile_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_schedule_block_by_id(db: DBSession, id: int) -> Optional[ProviderSchedule]:
    return db.query(ProviderSchedule).filter(ProviderSchedule.id == id).first()


def list_schedule_by_profile(
    db: DBSession, provider_profile_id: int, only_active: bool = True
) -> list[ProviderSchedule]:
    query = db.query(ProviderSchedule).filter(
        ProviderSchedule.provider_profile_id == provider_profile_id
    )
    if only_active:
        query = query.filter(ProviderSchedule.estado == ScheduleEstado.active)
    return query.all()


def deactivate_schedule_block(
    db: DBSession, block: ProviderSchedule
) -> ProviderSchedule:
    block.estado = ScheduleEstado.inactive
    db.add(block)
    db.commit()
    db.refresh(block)
    return block