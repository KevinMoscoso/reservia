import enum

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func

from app.models.shared.base import Base


class EquipoEstado(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    codigo = Column(String(100), nullable=False, unique=True)
    categoria = Column(String(100), nullable=False)
    estado = Column(
        Enum(EquipoEstado, name="equipoestado"),
        nullable=False,
        server_default=EquipoEstado.active.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )