from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogItemResponse(BaseModel):
    id: int
    actor_user_id: Optional[int]
    actor_full_name: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[int]
    metadata: Optional[dict]
    created_at: datetime


class AuditLogPageResponse(BaseModel):
    items: list[AuditLogItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int