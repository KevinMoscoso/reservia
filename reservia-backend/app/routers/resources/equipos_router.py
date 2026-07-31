from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep, require_role
from app.models.auth.user import User, UserRole
from app.schemas.resources.equipo import (
    EquipoCreateRequest,
    EquipoResponse,
    EquipoUpdateRequest,
)
from app.services.resources import equipo_service

router = APIRouter(prefix="/api/resources/equipos", tags=["equipos"])


@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def create_equipo(
    data: EquipoCreateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return equipo_service.create_equipo(db, data, actor_user_id=current_user.id)
    except equipo_service.CodigoAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/", response_model=list[EquipoResponse])
def list_equipos(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return equipo_service.list_equipos(db)


@router.patch("/{id}", response_model=EquipoResponse)
def update_equipo(
    id: int,
    data: EquipoUpdateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return equipo_service.update_equipo(db, id, data)
    except equipo_service.EquipoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{id}/deactivate", response_model=EquipoResponse)
def deactivate_equipo(
    id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return equipo_service.deactivate_equipo(db, id, actor_user_id=current_user.id)
    except equipo_service.EquipoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))