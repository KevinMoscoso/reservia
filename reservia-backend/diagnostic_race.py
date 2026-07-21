"""
Script de diagnostico para investigar el comportamiento de dos sesiones de
SQLAlchemy registrando el mismo email, SIN pytest de por medio.

Ejecutar desde reservia-backend/, con el venv activado:
    python -u diagnostic_race.py

El flag -u fuerza salida sin buffer: cada print aparece de inmediato,
sin importar el comportamiento de la terminal.
"""

print("Paso 1: importando modulos...", flush=True)

from app.core.database import SessionLocal, engine
from app.models.shared.base import Base
from app.models.auth.user import User
from app.schemas.auth.user import RegisterClientRequest
from app.services.auth import auth_service

print("Paso 1: OK", flush=True)

print("Paso 2: creando tablas si no existen...", flush=True)
Base.metadata.create_all(bind=engine, checkfirst=True)
print("Paso 2: OK", flush=True)

print("Paso 3: limpiando fila de prueba anterior si existe...", flush=True)
cleanup_session = SessionLocal()
cleanup_session.query(User).filter(User.email == "race_diag@example.com").delete()
cleanup_session.commit()
cleanup_session.close()
print("Paso 3: OK", flush=True)

data = RegisterClientRequest(
    email="race_diag@example.com", password="Secret123", full_name="Race Diagnostico"
)

print("Paso 4: abriendo session_a...", flush=True)
session_a = SessionLocal()
print("Paso 4: OK", flush=True)

print("Paso 5: abriendo session_b...", flush=True)
session_b = SessionLocal()
print("Paso 5: OK", flush=True)

print("Paso 6: llamando register_client(session_a)...", flush=True)
try:
    user_a = auth_service.register_client(session_a, data)
    print(f"Paso 6: OK, usuario creado con id={user_a.id}", flush=True)
except Exception as e:
    print(f"Paso 6: EXCEPCION: {type(e).__name__}: {e}", flush=True)

print("Paso 7: llamando register_client(session_b) (si algo se cuelga, es aqui)...", flush=True)
try:
    user_b = auth_service.register_client(session_b, data)
    print(f"Paso 7: OK (INESPERADO), usuario creado con id={user_b.id}", flush=True)
except Exception as e:
    print(f"Paso 7: EXCEPCION (se esperaba una): {type(e).__name__}: {e}", flush=True)

print("Paso 8: cerrando sesiones...", flush=True)
session_a.close()
session_b.close()
print("Paso 8: OK", flush=True)

print("Paso 9: limpiando fila de prueba...", flush=True)
cleanup_session = SessionLocal()
cleanup_session.query(User).filter(User.email == "race_diag@example.com").delete()
cleanup_session.commit()
cleanup_session.close()
print("Paso 9: OK", flush=True)

print("DIAGNOSTICO COMPLETADO SIN COLGARSE.", flush=True)