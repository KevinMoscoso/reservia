import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func

from app.models.shared.base import Base


class TipoNotificacion(str, enum.Enum):
    reserva_confirmada = "reserva_confirmada"
    cita_confirmada = "cita_confirmada"
    recordatorio = "recordatorio"


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False)
    tipo = Column(Enum(TipoNotificacion, name="tiponotificacion"), nullable=False)
    mensaje = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(BIGINT(unsigned=True), nullable=True)
    leida = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime, nullable=False, server_default=func.now())