from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import require_role
from app.models.auth.user import User, UserRole
from app.schemas.audit.audit import AuditLogPageResponse
from app.services.audit import audit_service

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/", response_model=AuditLogPageResponse)
def get_audit_log(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    if fecha_fin is None:
        fecha_fin = date.today()
    if fecha_inicio is None:
        fecha_inicio = fecha_fin - timedelta(days=30)

    report = audit_service.get_audit_log(db, fecha_inicio, fecha_fin, page, page_size)
    return AuditLogPageResponse(**report)