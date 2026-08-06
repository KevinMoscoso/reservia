"""
Script de seed de datos de prueba para Reservia.

Corre contra la base de datos REAL de desarrollo (reservia), usando la capa
de servicios existente del backend -- respeta hashing de contraseñas,
invariantes de negocio, y deja auditoria real, exactamente como si los datos
se hubieran creado a mano por la UI.

Es IDEMPOTENTE: se puede correr varias veces sin duplicar datos (busca por
email/codigo antes de crear).

Requiere que ya exista al menos un Administrador (creado via /setup).

Ejecutar UNA vez por sesion de pruebas, desde reservia-backend/, con el
venv activado:
    python seed_data.py
"""
from datetime import date, datetime, time, timedelta

from app.core.database import SessionLocal
from app.models.auth.user import User, UserRole
from app.repositories.auth import user_repository
from app.repositories.resources import equipo_repository, sala_repository
from app.schemas.auth.user import CreateProviderRequest, RegisterClientRequest
from app.schemas.providers.provider import (
    ProviderProfileUpdateRequest,
    ScheduleBlockCreateRequest,
)
from app.schemas.reservations.reserva import BookingCreateRequest
from app.schemas.resources.equipo import EquipoCreateRequest
from app.schemas.resources.sala import SalaCreateRequest
from app.services.auth import auth_service
from app.services.providers import provider_service
from app.services.reservations import reserva_sala_service
from app.services.resources import equipo_service, sala_service

PASSWORD = "Secret123"


def _next_weekday(target_weekday: int) -> date:
    # 0=lunes ... 6=domingo (igual que date.weekday())
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def get_or_create_client(db, email, full_name):
    existing = user_repository.get_by_email(db, email)
    if existing is not None:
        print(f"  [existe] cliente {email}")
        return existing

    data = RegisterClientRequest(email=email, password=PASSWORD, full_name=full_name)
    user = auth_service.register_client(db, data)
    db.commit()
    print(f"  [creado] cliente {email}")
    return user


def get_or_create_provider(db, admin_user, email, full_name):
    existing = user_repository.get_by_email(db, email)
    if existing is not None:
        print(f"  [existe] proveedor {email}")
        return existing

    data = CreateProviderRequest(email=email, password=PASSWORD, full_name=full_name)
    user = auth_service.create_provider(db, admin_user=admin_user, data=data)
    db.commit()
    print(f"  [creado] proveedor {email}")
    return user


def ensure_provider_setup(db, provider_user, slot_duration_minutes, schedule_blocks):
    profile = provider_service.get_own_profile(db, provider_user)

    if profile.slot_duration_minutes != slot_duration_minutes:
        provider_service.update_own_profile(
            db,
            provider_user,
            ProviderProfileUpdateRequest(slot_duration_minutes=slot_duration_minutes),
        )
        db.commit()
        print(f"    duracion de slot configurada: {slot_duration_minutes} min")

    for day_of_week, start_str, end_str in schedule_blocks:
        start_t = datetime.strptime(start_str, "%H:%M").time()
        end_t = datetime.strptime(end_str, "%H:%M").time()
        try:
            provider_service.add_schedule_block(
                db,
                provider_user,
                ScheduleBlockCreateRequest(
                    day_of_week=day_of_week, start_time=start_t, end_time=end_t
                ),
            )
            db.commit()
            print(f"    bloque agregado: {day_of_week} {start_str}-{end_str}")
        except provider_service.ScheduleOverlapError:
            db.rollback()
            print(f"    [existe] bloque {day_of_week} {start_str}-{end_str}")

    return provider_service.get_own_profile(db, provider_user)


def get_or_create_sala(db, nombre, ubicacion, capacidad, admin_user_id):
    for sala in sala_repository.list_all(db):
        if sala.nombre == nombre:
            print(f"  [existe] sala '{nombre}' (id={sala.id})")
            return sala

    sala = sala_service.create_sala(
        db,
        SalaCreateRequest(nombre=nombre, ubicacion=ubicacion, capacidad=capacidad),
        actor_user_id=admin_user_id,
    )
    db.commit()
    print(f"  [creada] sala '{nombre}' (id={sala.id})")
    return sala


def get_or_create_equipo(db, nombre, codigo, categoria, admin_user_id):
    existing = equipo_repository.get_by_codigo(db, codigo)
    if existing is not None:
        print(f"  [existe] equipo '{nombre}' (id={existing.id})")
        return existing

    equipo = equipo_service.create_equipo(
        db,
        EquipoCreateRequest(nombre=nombre, codigo=codigo, categoria=categoria),
        actor_user_id=admin_user_id,
    )
    db.commit()
    print(f"  [creado] equipo '{nombre}' (id={equipo.id})")
    return equipo


def main():
    db = SessionLocal()

    print("Buscando Administrador existente...")
    admin = db.query(User).filter(User.role == UserRole.admin).first()
    if admin is None:
        print(
            "\nERROR: no existe ningun usuario con rol admin en la base de datos "
            "'reservia'. Crea uno primero via POST /api/auth/setup (o desde la "
            "pantalla /setup del frontend) y vuelve a correr este script."
        )
        db.close()
        return
    print(f"  Administrador encontrado: {admin.email} (id={admin.id})\n")

    print("Creando/verificando proveedores...")
    provider1 = get_or_create_provider(
        db, admin, "seed.provider1@reservia.com", "Dr. Seed Perez"
    )
    provider2 = get_or_create_provider(
        db, admin, "seed.provider2@reservia.com", "Lic. Seed Gomez"
    )
    print()

    print("Configurando horario de Dr. Seed Perez (slots de 30 min, con hueco de almuerzo)...")
    profile1 = ensure_provider_setup(
        db,
        provider1,
        slot_duration_minutes=30,
        schedule_blocks=[
            ("monday", "09:00", "12:00"),
            ("monday", "14:00", "17:00"),
            ("tuesday", "09:00", "12:00"),
            ("tuesday", "14:00", "17:00"),
            ("wednesday", "09:00", "12:00"),
            ("wednesday", "14:00", "17:00"),
            ("thursday", "09:00", "12:00"),
            ("thursday", "14:00", "17:00"),
            ("friday", "09:00", "12:00"),
            ("friday", "14:00", "17:00"),
        ],
    )
    print()

    print("Configurando horario de Lic. Seed Gomez (slots de 45 min, con hueco de almuerzo)...")
    profile2 = ensure_provider_setup(
        db,
        provider2,
        slot_duration_minutes=45,
        schedule_blocks=[
            ("monday", "10:00", "13:00"),
            ("wednesday", "10:00", "13:00"),
            ("friday", "10:00", "13:00"),
        ],
    )
    print()

    print("Creando/verificando clientes...")
    client1 = get_or_create_client(db, "seed.client1@reservia.com", "Cliente Seed Uno")
    client2 = get_or_create_client(db, "seed.client2@reservia.com", "Cliente Seed Dos")
    print()

    print("Creando/verificando salas...")
    sala1 = get_or_create_sala(db, "Sala de Juntas A", "Piso 1", 10, admin.id)
    sala2 = get_or_create_sala(db, "Sala de Conferencias B", "Piso 2", 25, admin.id)
    print()

    print("Creando/verificando equipos...")
    equipo1 = get_or_create_equipo(db, "Proyector Epson X100", "EQ-SEED-001", "AV", admin.id)
    equipo2 = get_or_create_equipo(db, "Laptop Dell Seed", "EQ-SEED-002", "Computo", admin.id)
    print()

    print("Creando reserva de sala ya confirmada (para probar solapamiento desde la UI)...")
    fecha_reserva = date.today() + timedelta(days=3)
    try:
        reserva = reserva_sala_service.create_reserva(
            db,
            sala1.id,
            client1.id,
            BookingCreateRequest(
                fecha=fecha_reserva,
                hora_inicio=time(10, 0),
                num_bloques=1,
                motivo="Reunion de seed -- intenta reservar este mismo bloque para ver el error 409",
            ),
        )
        print(
            f"  [creada] reserva de '{sala1.nombre}' el {fecha_reserva} 10:00-10:30 "
            f"(cliente: seed.client1@reservia.com)"
        )
    except reserva_sala_service.OverlapError:
        db.rollback()
        print(f"  [existe] reserva de '{sala1.nombre}' el {fecha_reserva} 10:00-10:30")
    print()

    print("Creando reserva ya cancelada (para ver el estilo atenuado en Mis reservas)...")
    fecha_cancelada = date.today() + timedelta(days=4)
    try:
        reserva_cancelada = reserva_sala_service.create_reserva(
            db,
            sala2.id,
            client1.id,
            BookingCreateRequest(
                fecha=fecha_cancelada,
                hora_inicio=time(11, 0),
                num_bloques=1,
                motivo="Reunion de seed que sera cancelada",
            ),
        )
        reserva_sala_service.cancel_reserva(db, reserva_cancelada.id, actor_user=client1)
        print(f"  [creada y cancelada] reserva de '{sala2.nombre}' el {fecha_cancelada} 11:00")
    except reserva_sala_service.OverlapError:
        db.rollback()
        print(f"  [existe] reserva de '{sala2.nombre}' el {fecha_cancelada} 11:00")
    print()

    print("Creando cita confirmada con Dr. Seed Perez...")
    fecha_cita = _next_weekday(0)  # proximo lunes
    from app.services.reservations import cita_service

    try:
        cita = cita_service.create_cita(
            db,
            profile1.id,
            client2.id,
            BookingCreateRequest(
                fecha=fecha_cita,
                hora_inicio=time(9, 0),
                num_bloques=1,
                motivo="Consulta de seed",
            ),
        )
        print(
            f"  [creada] cita con Dr. Seed Perez el {fecha_cita} (lunes) 09:00-09:30 "
            f"(cliente: seed.client2@reservia.com)"
        )
    except cita_service.OverlapError:
        db.rollback()
        print(f"  [existe] cita con Dr. Seed Perez el {fecha_cita} 09:00")

    db.close()

    print("\n" + "=" * 60)
    print("SEED COMPLETADO")
    print("=" * 60)
    print(f"\nContraseña para TODAS las cuentas creadas: {PASSWORD}\n")
    print("Cuentas:")
    print("  Proveedor 1 (slots 30 min, huecos lun-vie): seed.provider1@reservia.com")
    print("  Proveedor 2 (slots 45 min, lun/mie/vie 10-13): seed.provider2@reservia.com")
    print("  Cliente 1 (tiene 1 reserva confirmada + 1 cancelada): seed.client1@reservia.com")
    print("  Cliente 2 (tiene 1 cita confirmada): seed.client2@reservia.com")
    print("\nRecursos:")
    print(f"  Sala 1: '{sala1.nombre}' -- bloqueada el {fecha_reserva} 10:00-10:30")
    print(f"  Sala 2: '{sala2.nombre}'")
    print(f"  Equipo 1: '{equipo1.nombre}' (codigo {equipo1.codigo})")
    print(f"  Equipo 2: '{equipo2.nombre}' (codigo {equipo2.codigo})")
    print(
        f"\nPara probar el error de solapamiento (409): inicia sesion con cualquier "
        f"cuenta, ve a '{sala1.nombre}', fecha {fecha_reserva}, e intenta reservar "
        f"el bloque de las 10:00."
    )


if __name__ == "__main__":
    main()