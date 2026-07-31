import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Time
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.shared.base import Base


class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class ScheduleEstado(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class ProviderSchedule(Base):
    __tablename__ = "provider_schedules"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    provider_profile_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("provider_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week = Column(Enum(DayOfWeek, name="dayofweek"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    estado = Column(
        Enum(ScheduleEstado, name="scheduleestado"),
        nullable=False,
        server_default=ScheduleEstado.active.value,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    provider_profile = relationship("ProviderProfile")