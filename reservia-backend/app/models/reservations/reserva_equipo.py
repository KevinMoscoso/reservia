from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String, Time
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.reservations.reserva_sala import EstadoReserva
from app.models.shared.base import Base


class ReservaEquipo(Base):
    __tablename__ = "reservas_equipos"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    equipo_id = Column(BIGINT(unsigned=True), ForeignKey("equipos.id"), nullable=False)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    motivo = Column(String(255), nullable=False)
    estado = Column(
        Enum(EstadoReserva, name="estadoreserva_equipo"),
        nullable=False,
        server_default=EstadoReserva.pendiente.value,
    )
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    equipo = relationship("Equipo")
    user = relationship("User", foreign_keys=[user_id])