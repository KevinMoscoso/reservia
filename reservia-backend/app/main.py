from fastapi import FastAPI

from app.routers.auth.admin_users_router import router as admin_users_router
from app.routers.auth.auth_router import router as auth_router

app = FastAPI(title="Reservia API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(admin_users_router)