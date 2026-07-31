from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.shared.base import Base


class ProviderProfile(Base):
    __tablename__ = "provider_profiles"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    slot_duration_minutes = Column(
        SMALLINT(unsigned=True), nullable=False, server_default="30"
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")