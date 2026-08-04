from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep, require_role
from app.models.auth.user import User, UserRole
from app.schemas.reservations.reserva import (
    AvailabilityBlockResponse,
    BookingCreateRequest,
    ReservaEquipoResponse,
)
from app.schemas.resources.equipo import (
    EquipoCreateRequest,
    EquipoResponse,
    EquipoUpdateRequest,
)
from app.services.reservations import reserva_equipo_service
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


@router.get("/reservas/me", response_model=list[ReservaEquipoResponse])
def list_my_reservas_equipos(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return reserva_equipo_service.list_my_reservas(db, current_user.id)


@router.patch("/reservas/{reserva_id}/cancel", response_model=ReservaEquipoResponse)
def cancel_reserva_equipo(
    reserva_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_equipo_service.cancel_reserva(db, reserva_id, actor_user=current_user)
    except reserva_equipo_service.ReservaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except reserva_equipo_service.NotOwnerOrAdminError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("/{id}/availability", response_model=list[AvailabilityBlockResponse])
def get_equipo_availability(
    id: int,
    fecha: date = Query(...),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_equipo_service.get_availability(db, id, fecha)
    except reserva_equipo_service.EquipoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/{id}/reservas",
    response_model=ReservaEquipoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reserva_equipo(
    id: int,
    data: BookingCreateRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return reserva_equipo_service.create_reserva(db, id, current_user.id, data)
    except reserva_equipo_service.EquipoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (
        reserva_equipo_service.EquipoInactiveError,
        reserva_equipo_service.InvalidDateError,
        reserva_equipo_service.MisalignedTimeError,
        reserva_equipo_service.OutOfHoursError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    except reserva_equipo_service.OverlapError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


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