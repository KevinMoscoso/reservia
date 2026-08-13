from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep
from app.models.auth.user import User
from app.schemas.notifications.notificacion import NotificacionResponse, UnreadCountResponse
from app.services.notifications import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/me", response_model=list[NotificacionResponse])
def list_my_notifications(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return notification_service.list_my_notifications(db, current_user.id)


@router.get("/me/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    count = notification_service.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/me/read-all")
def mark_all_as_read(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    notification_service.mark_all_as_read(db, current_user.id)
    return {"detail": "ok"}


@router.patch("/{id}/read", response_model=NotificacionResponse)
def mark_notification_as_read(
    id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    try:
        return notification_service.mark_notification_as_read(db, id, current_user.id)
    except notification_service.NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except notification_service.NotOwnerError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))