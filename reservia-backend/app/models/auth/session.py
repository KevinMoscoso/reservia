from sqlalchemy import CHAR, Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.shared.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(CHAR(64), primary_key=True)
    user_id = Column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    last_seen_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User")