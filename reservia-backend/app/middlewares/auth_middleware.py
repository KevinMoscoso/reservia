from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from app.core import config
from app.core.database import get_db
from app.models.auth.user import User
from app.services.auth import auth_service


def get_current_user_dep(request: Request, db: DBSession = Depends(get_db)) -> User:
    token = request.cookies.get(config.SESSION_COOKIE_NAME)
    try:
        return auth_service.get_current_user(db, token)
    except (auth_service.NotAuthenticatedError, auth_service.SessionExpiredError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


def require_role(*roles: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user_dep)) -> User:
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para este recurso",
            )
        return current_user

    return dependency