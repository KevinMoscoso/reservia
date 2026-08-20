from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session as DBSession, aliased

from app.models.auth.user import User
from app.models.shared.audit_log import AuditLog


def log_action(
    db: DBSession,
    actor_user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    metadata: Optional[dict],
) -> None:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_=metadata,
    )
    db.add(entry)
    db.commit()


def list_paginated(db: DBSession, fecha_inicio: date, fecha_fin: date, page: int, page_size: int):
    """
    Retorna (items, total) donde items es una lista de tuplas
    (AuditLog, actor_full_name_o_None), ordenadas por created_at descendente.
    """
    start_dt = datetime.combine(fecha_inicio, time.min)
    end_dt = datetime.combine(fecha_fin + timedelta(days=1), time.min)

    base_query = (
        db.query(AuditLog, User.full_name)
        .outerjoin(User, AuditLog.actor_user_id == User.id)
        .filter(AuditLog.created_at >= start_dt, AuditLog.created_at < end_dt)
    )

    total = base_query.count()

    items = (
        base_query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total