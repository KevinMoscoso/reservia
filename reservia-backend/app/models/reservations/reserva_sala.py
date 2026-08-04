import enum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String, Time
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.shared.base import Base


class EstadoReserva(str, enum.Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"


class ReservaSala(Base):
    __tablename__ = "reservas_salas"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    sala_id = Column(BIGINT(unsigned=True), ForeignKey("salas.id"), nullable=False)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    motivo = Column(String(255), nullable=False)
    estado = Column(
        Enum(EstadoReserva, name="estadoreserva_sala"),
        nullable=False,
        server_default=EstadoReserva.pendiente.value,
    )
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sala = relationship("Sala")
    user = relationship("User", foreign_keys=[user_id])