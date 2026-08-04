from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep, require_role
from app.models.auth.user import User, UserRole
from app.schemas.reservations.reserva import (
    AvailabilityBlockResponse,
    BookingCreateRequest,
    ReservaSalaResponse,
)
from app.schemas.resources.sala import SalaCreateRequest, SalaResponse, SalaUpdateRequest
from app.services.reservations import reserva_sala_service
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


@router.get("/reservas/me", response_model=list[ReservaSalaResponse])
def list_my_reservas_salas(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return reserva_sala_service.list_my_reservas(db, current_user.id)


@router.patch("/reservas/{reserva_id}/cancel", response_model=ReservaSalaResponse)
def cancel_reserva_sala(
    reserva_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_sala_service.cancel_reserva(db, reserva_id, actor_user=current_user)
    except reserva_sala_service.ReservaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except reserva_sala_service.NotOwnerOrAdminError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("/{id}/availability", response_model=list[AvailabilityBlockResponse])
def get_sala_availability(
    id: int,
    fecha: date = Query(...),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_sala_service.get_availability(db, id, fecha)
    except reserva_sala_service.SalaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/{id}/reservas",
    response_model=ReservaSalaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reserva_sala(
    id: int,
    data: BookingCreateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_sala_service.create_reserva(db, id, current_user.id, data)
    except reserva_sala_service.SalaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (
        reserva_sala_service.SalaInactiveError,
        reserva_sala_service.InvalidDateError,
        reserva_sala_service.MisalignedTimeError,
        reserva_sala_service.OutOfHoursError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    except reserva_sala_service.OverlapError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


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