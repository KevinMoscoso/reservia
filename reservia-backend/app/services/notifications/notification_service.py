from typing import Optional

from app.models.notifications.notificacion import Notificacion
from app.repositories.notifications import notification_repository


class NotificationNotFoundError(Exception):
    pass


class NotOwnerError(Exception):
    pass


def create_notification(
    db,
    user_id: int,
    tipo,
    mensaje: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
) -> Notificacion:
    return notification_repository.create(db, user_id, tipo, mensaje, entity_type, entity_id)


def list_my_notifications(db, user_id: int) -> list[Notificacion]:
    return notification_repository.list_by_user(db, user_id)


def get_unread_count(db, user_id: int) -> int:
    return notification_repository.count_unread_by_user(db, user_id)


def mark_notification_as_read(db, notification_id: int, user_id: int) -> Notificacion:
    notif = notification_repository.get_by_id(db, notification_id)
    if notif is None:
        raise NotificationNotFoundError("notificacion no encontrada")
    if notif.user_id != user_id:
        raise NotOwnerError("no tienes permiso sobre esta notificacion")
    if notif.leida:
        return notif
    return notification_repository.mark_read(db, notif)


def mark_all_as_read(db, user_id: int) -> None:
    notification_repository.mark_all_read_by_user(db, user_id)