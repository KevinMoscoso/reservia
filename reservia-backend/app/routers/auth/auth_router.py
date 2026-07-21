from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session as DBSession

from app.core import config
from app.core.database import get_db
from app.middlewares.auth_middleware import get_current_user_dep
from app.models.auth.user import User
from app.schemas.auth.user import (
    LoginRequest,
    RegisterClientRequest,
    SetupAdminRequest,
    UserResponse,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterClientRequest, db: DBSession = Depends(get_db)):
    try:
        return auth_service.register_client(db, data)
    except auth_service.EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/setup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def setup(data: SetupAdminRequest, db: DBSession = Depends(get_db)):
    try:
        return auth_service.bootstrap_admin(db, data)
    except auth_service.SystemAlreadyInitializedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post("/login", response_model=UserResponse)
def login(data: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    try:
        user, token = auth_service.login(db, data)
    except auth_service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except auth_service.AccountLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except auth_service.AccountInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=config.SESSION_COOKIE_SECURE,
    )
    return user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(request: Request, response: Response, db: DBSession = Depends(get_db)):
    token = request.cookies.get(config.SESSION_COOKIE_NAME)
    if token is not None:
        auth_service.logout(db, token)
    response.delete_cookie(key=config.SESSION_COOKIE_NAME)
    return {"detail": "logout ok"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user_dep)):
    return current_user