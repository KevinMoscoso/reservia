import enum

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.sql import func

from app.models.shared.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    provider = "provider"
    client = "client"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(Enum(UserRole, name="userrole"), nullable=False)
    status = Column(
        Enum(UserStatus, name="userstatus"),
        nullable=False,
        server_default=UserStatus.active.value,
    )
    failed_login_attempts = Column(
        TINYINT(unsigned=True), nullable=False, server_default="0"
    )
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )