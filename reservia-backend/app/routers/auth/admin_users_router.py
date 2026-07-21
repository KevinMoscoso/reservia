from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import require_role
from app.models.auth.user import User, UserRole
from app.schemas.auth.user import CreateProviderRequest, UserResponse
from app.services.auth import auth_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/providers", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    data: CreateProviderRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    try:
        return auth_service.create_provider(db, admin_user=current_user, data=data)
    except auth_service.EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))