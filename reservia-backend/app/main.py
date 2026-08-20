from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.core import config
from app.routers.audit.audit_router import router as audit_router
from app.routers.auth.admin_users_router import router as admin_users_router
from app.routers.auth.auth_router import router as auth_router
from app.routers.notifications.notifications_router import router as notifications_router
from app.routers.providers.providers_router import router as providers_router
from app.routers.reports.reports_router import router as reports_router
from app.routers.resources.equipos_router import router as equipos_router
from app.routers.resources.salas_router import router as salas_router
from app.services.notifications.reminder_job import check_and_send_reminders

scheduler = BackgroundScheduler()
_scheduler_started = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_started
    if not _scheduler_started:
        scheduler.add_job(
            check_and_send_reminders, "interval",
            minutes=config.REMINDER_CHECK_INTERVAL_MINUTES,
            id="reminder_job", replace_existing=True,
        )
        scheduler.start()
        _scheduler_started = True
    yield


app = FastAPI(title="Reservia API", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(salas_router)
app.include_router(equipos_router)
app.include_router(providers_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(audit_router)