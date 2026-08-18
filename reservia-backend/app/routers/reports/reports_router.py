from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.middlewares.auth_middleware import require_role
from app.models.auth.user import User, UserRole
from app.schemas.reports.report import (
    OccupancyReportResponse, ProviderActivityReportResponse, SystemActivityReportResponse,
)
from app.services.reports import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _resolve_dates(fecha_inicio, fecha_fin):
    if fecha_fin is None:
        fecha_fin = date.today()
    if fecha_inicio is None:
        fecha_inicio = fecha_fin - timedelta(days=30)
    return fecha_inicio, fecha_fin


@router.get("/occupancy")
def get_occupancy_report(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    format: str = Query("json"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    fecha_inicio, fecha_fin = _resolve_dates(fecha_inicio, fecha_fin)
    report = report_service.get_occupancy_report(db, fecha_inicio, fecha_fin)
    if format == "csv":
        return Response(
            content=report_service.occupancy_report_to_csv(report),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=ocupacion_recursos.csv"},
        )
    return OccupancyReportResponse(**report)


@router.get("/providers")
def get_provider_activity_report(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    format: str = Query("json"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value, UserRole.provider.value)),
):
    fecha_inicio, fecha_fin = _resolve_dates(fecha_inicio, fecha_fin)
    report = report_service.get_provider_activity_report(db, fecha_inicio, fecha_fin, current_user)
    if format == "csv":
        return Response(
            content=report_service.provider_activity_report_to_csv(report),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=actividad_proveedores.csv"},
        )
    return ProviderActivityReportResponse(**report)


@router.get("/system")
def get_system_activity_report(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    format: str = Query("json"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin.value)),
):
    fecha_inicio, fecha_fin = _resolve_dates(fecha_inicio, fecha_fin)
    report = report_service.get_system_activity_report(db, fecha_inicio, fecha_fin)
    if format == "csv":
        return Response(
            content=report_service.system_activity_report_to_csv(report),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=actividad_sistema.csv"},
        )
    return SystemActivityReportResponse(**report)