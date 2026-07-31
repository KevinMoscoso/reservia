import enum

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.sql import func

from app.models.shared.base import Base


class SalaEstado(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Sala(Base):
    __tablename__ = "salas"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    capacidad = Column(INTEGER(unsigned=True), nullable=False)
    estado = Column(
        Enum(SalaEstado, name="salaestado"),
        nullable=False,
        server_default=SalaEstado.active.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )