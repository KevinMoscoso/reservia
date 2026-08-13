"""
Diagnostico: por que check_and_send_reminders() no marca la reserva de
prueba como recordatorio_enviado=True ni crea la notificacion.

Ejecutar desde reservia-backend/, con el venv activado:
    python -u diagnostic_reminder.py

Usa la base de datos reservia_test (la misma que usan los tests), y NO
depende de pytest ni de MySQL real -- solo de que reservia_test exista y
tenga las tablas creadas (las crea si no existen).
"""
from datetime import datetime, timedelta

from app.core import config
from app.models.auth.user import User
from app.models.resources.sala import Sala
from app.models.reservations.reserva_sala import ReservaSala, EstadoReserva
from app.models.shared.base import Base
from app.schemas.auth.user import SetupAdminRequest, RegisterClientRequest
from app.schemas.resources.sala import SalaCreateRequest
from app.services.auth import auth_service
from app.services.resources import sala_service

from tests.conftest import TestSessionLocal, test_engine

print("Paso 1: creando tablas en reservia_test si no existen...", flush=True)
Base.metadata.create_all(bind=test_engine, checkfirst=True)
print("Paso 1: OK", flush=True)

db = TestSessionLocal()

print("Paso 2: limpiando datos de un run anterior de este script...", flush=True)
db.query(ReservaSala).delete()
db.query(Sala).filter(Sala.nombre == "Sala Diag").delete()
db.query(User).filter(
    User.email.in_(["diag_admin@example.com", "diag_client@example.com"])
).delete(synchronize_session=False)
db.commit()
print("Paso 2: OK", flush=True)

print("Paso 3: creando admin, sala y cliente de prueba...", flush=True)
admin = auth_service.bootstrap_admin(
    db,
    SetupAdminRequest(email="diag_admin@example.com", password="Secret123", full_name="Diag Admin"),
)
db.commit()

sala = sala_service.create_sala(
    db,
    SalaCreateRequest(nombre="Sala Diag", ubicacion="Piso 1", capacidad=5),
    actor_user_id=admin.id,
)
db.commit()

client = auth_service.register_client(
    db,
    RegisterClientRequest(email="diag_client@example.com", password="Secret123", full_name="Diag Client"),
)
db.commit()
print(f"Paso 3: OK (admin.id={admin.id}, sala.id={sala.id}, client.id={client.id})", flush=True)

print("Paso 4: creando reserva confirmada 30 min en el futuro...", flush=True)
now = datetime.now()
upcoming_start = now + timedelta(minutes=30)

reserva = ReservaSala(
    sala_id=sala.id,
    user_id=client.id,
    fecha=upcoming_start.date(),
    hora_inicio=upcoming_start.time().replace(microsecond=0),
    hora_fin=(upcoming_start + timedelta(minutes=30)).time().replace(microsecond=0),
    motivo="Diagnostico",
    estado=EstadoReserva.confirmada,
    recordatorio_enviado=False,
)
db.add(reserva)
db.commit()
db.refresh(reserva)
print(
    f"Paso 4: OK -- reserva id={reserva.id} fecha={reserva.fecha} "
    f"hora_inicio={reserva.hora_inicio} estado={reserva.estado} "
    f"recordatorio_enviado={reserva.recordatorio_enviado}",
    flush=True,
)

db.close()
print("Paso 5: sesion de escritura cerrada.", flush=True)

print("Paso 6: abriendo una SEGUNDA sesion (igual que hace el job) y consultando...", flush=True)
db2 = TestSessionLocal()

pendientes = (
    db2.query(ReservaSala)
    .filter(
        ReservaSala.estado == EstadoReserva.confirmada,
        ReservaSala.recordatorio_enviado == False,  # noqa: E712
    )
    .all()
)

print(f"Paso 6: pendientes encontradas = {len(pendientes)}", flush=True)
for r in pendientes:
    print(
        f"    id={r.id} fecha={r.fecha} hora_inicio={r.hora_inicio} "
        f"estado={r.estado} recordatorio_enviado={r.recordatorio_enviado}",
        flush=True,
    )

now2 = datetime.now()
threshold2 = now2 + timedelta(hours=config.REMINDER_HOURS_BEFORE)
print(f"Paso 7: now (job)={now2}", flush=True)
print(f"Paso 7: threshold (job)={threshold2}", flush=True)

for r in pendientes:
    inicio = datetime.combine(r.fecha, r.hora_inicio)
    condicion = now2 <= inicio <= threshold2
    print(f"Paso 8: reserva id={r.id}: inicio={inicio} -> now<=inicio<=threshold = {condicion}", flush=True)

db2.close()
print("DIAGNOSTICO COMPLETADO.", flush=True)