from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep, require_role
from app.models.auth.user import User, UserRole
from app.schemas.resources.sala import SalaCreateRequest, SalaResponse, SalaUpdateRequest
from app.services.resources import sala_service

router = APIRouter(prefix="/api/resources/salas", tags=["salas"])


@router.post("/", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def create_sala(
    data: SalaCreateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    return sala_service.create_sala(db, data, actor_user_id=current_user.id)


@router.get("/", response_model=list[SalaResponse])
def list_salas(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return sala_service.list_salas(db)


@router.patch("/{id}", response_model=SalaResponse)
def update_sala(
    id: int,
    data: SalaUpdateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return sala_service.update_sala(db, id, data)
    except sala_service.SalaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{id}/deactivate", response_model=SalaResponse)
def deactivate_sala(
    id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return sala_service.deactivate_sala(db, id, actor_user_id=current_user.id)
    except sala_service.SalaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))