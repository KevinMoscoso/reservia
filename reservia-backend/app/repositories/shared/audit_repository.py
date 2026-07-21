from typing import Optional

from sqlalchemy.orm import Session as DBSession

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