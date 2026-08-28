import enum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.shared.base import Base


class DateBlockEstado(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class ProviderDateBlock(Base):
    __tablename__ = "provider_date_blocks"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    provider_profile_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("provider_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha = Column(Date, nullable=False)
    motivo = Column(String(255), nullable=True)
    estado = Column(
        Enum(DateBlockEstado, name="datablockestado"),
        nullable=False,
        server_default=DateBlockEstado.active.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    provider_profile = relationship("ProviderProfile")