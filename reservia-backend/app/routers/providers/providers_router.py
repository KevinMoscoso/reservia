from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep, require_role
from app.models.auth.user import User, UserRole
from app.schemas.providers.provider import (
    ProviderProfileResponse,
    ProviderProfileUpdateRequest,
    ProviderPublicResponse,
    ScheduleBlockCreateRequest,
    ScheduleBlockResponse,
)
from app.services.providers import provider_service

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("/", response_model=list[ProviderPublicResponse])
def list_providers(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    results = provider_service.list_public_providers(db)
    return [
        ProviderPublicResponse(
            id=profile.id,
            user_id=profile.user_id,
            full_name=user.full_name,
            slot_duration_minutes=profile.slot_duration_minutes,
        )
        for profile, user in results
    ]


@router.get("/me/profile", response_model=ProviderProfileResponse)
def get_my_profile(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.provider.value)),
):
    return provider_service.get_own_profile(db, current_user)


@router.put("/me/profile", response_model=ProviderProfileResponse)
def update_my_profile(
    data: ProviderProfileUpdateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.provider.value)),
):
    return provider_service.update_own_profile(db, current_user, data)


@router.get("/me/schedule", response_model=list[ScheduleBlockResponse])
def get_my_schedule(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.provider.value)),
):
    return provider_service.list_own_schedule(db, current_user)


@router.post(
    "/me/schedule",
    response_model=ScheduleBlockResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_my_schedule_block(
    data: ScheduleBlockCreateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.provider.value)),
):
    try:
        return provider_service.add_schedule_block(db, current_user, data)
    except provider_service.ScheduleOverlapError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/me/schedule/{id}/deactivate", response_model=ScheduleBlockResponse)
def deactivate_my_schedule_block(
    id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.provider.value)),
):
    try:
        return provider_service.deactivate_own_schedule_block(db, current_user, id)
    except provider_service.NotScheduleOwnerError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except provider_service.ScheduleBlockNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{provider_profile_id}/schedule", response_model=list[ScheduleBlockResponse])
def get_public_schedule(
    provider_profile_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return provider_service.get_public_schedule(db, provider_profile_id)
    except provider_service.ProviderProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))