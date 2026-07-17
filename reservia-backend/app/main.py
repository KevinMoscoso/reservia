"""
Punto de entrada de la aplicacion.
NOTA: este archivo es un placeholder de verificacion.
Chat B lo reemplazara/extendera al implementar el modulo Auth & Roles
(registro de auth_router y admin_users_router).
"""
from fastapi import FastAPI

app = FastAPI(title="Reservia API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
