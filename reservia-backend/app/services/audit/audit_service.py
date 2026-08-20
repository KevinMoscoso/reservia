import math
from datetime import date

from app.repositories.shared import audit_repository


def get_audit_log(db, fecha_inicio: date, fecha_fin: date, page: int, page_size: int) -> dict:
    rows, total = audit_repository.list_paginated(db, fecha_inicio, fecha_fin, page, page_size)

    items = [
        {
            "id": log.id,
            "actor_user_id": log.actor_user_id,
            "actor_full_name": actor_full_name,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "metadata": log.metadata_,
            "created_at": log.created_at,
        }
        for log, actor_full_name in rows
    ]

    total_pages = math.ceil(total / page_size) if page_size else 0

    return {
        "items": items, "total": total, "page": page,
        "page_size": page_size, "total_pages": total_pages,
    }