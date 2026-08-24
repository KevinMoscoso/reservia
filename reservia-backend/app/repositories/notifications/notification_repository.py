from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.notifications.notificacion import Notificacion, TipoNotificacion


def create(
    db: DBSession,
    user_id: int,
    tipo: TipoNotificacion,
    mensaje: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
) -> Notificacion:
    notif = Notificacion(
        user_id=user_id,
        tipo=tipo,
        mensaje=mensaje,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_by_id(db: DBSession, id: int) -> Optional[Notificacion]:
    return db.query(Notificacion).filter(Notificacion.id == id).first()


def list_by_user_paginated(db: DBSession, user_id: int, page: int, page_size: int):
    query = (
        db.query(Notificacion)
        .filter(Notificacion.user_id == user_id)
        .order_by(Notificacion.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def count_unread_by_user(db: DBSession, user_id: int) -> int:
    return (
        db.query(Notificacion)
        .filter(Notificacion.user_id == user_id, Notificacion.leida == False)  # noqa: E712
        .count()
    )


def mark_read(db: DBSession, notif: Notificacion) -> Notificacion:
    notif.leida = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_read_by_user(db: DBSession, user_id: int) -> None:
    db.query(Notificacion).filter(
        Notificacion.user_id == user_id, Notificacion.leida == False  # noqa: E712
    ).update({"leida": True})
    db.commit()