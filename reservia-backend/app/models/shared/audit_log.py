from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT, JSON
from sqlalchemy.sql import func

from app.models.shared.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    actor_user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BIGINT(unsigned=True), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())