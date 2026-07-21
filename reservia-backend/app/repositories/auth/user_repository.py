from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.models.auth.user import User, UserRole, UserStatus


def get_by_email(db: DBSession, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: DBSession, id: int) -> Optional[User]:
    return db.query(User).filter(User.id == id).first()


def create_user(
    db: DBSession,
    email: str,
    password_hash: str,
    full_name: str,
    role: UserRole,
    status: UserStatus = UserStatus.active,
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        status=status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def count_by_role(db: DBSession, role: UserRole) -> int:
    return db.query(func.count(User.id)).filter(User.role == role).scalar()


def increment_failed_attempts(db: DBSession, user: User) -> User:
    user.failed_login_attempts += 1
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_failed_attempts(db: DBSession, user: User) -> User:
    user.failed_login_attempts = 0
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_locked_until(db: DBSession, user: User, until: datetime) -> User:
    user.locked_until = until
    db.add(user)
    db.commit()
    db.refresh(user)
    return user