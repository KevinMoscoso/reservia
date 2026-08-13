from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.notifications.notificacion import TipoNotificacion


class NotificacionResponse(BaseModel):
    id: int
    tipo: TipoNotificacion
    mensaje: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    leida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    count: int