import threading
from datetime import date, time, timedelta

from app.core import config
from app.schemas.reservations.reserva import BookingCreateRequest
from app.services.reservations import reserva_sala_service
from tests.conftest import TestSessionLocal


def _setup_admin(client, email="admin_reservas_salas@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reservas"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email="cliente_reservas_salas@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Reservas"},
    )
    return _login_as(client, email)


def _create_sala(client, nombre="Sala Test"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _future_date():
    return (date.today() + timedelta(days=7)).isoformat()


def test_availability_endpoint_shows_free_and_booked_blocks(client):
    _setup_admin(client, email="admin_avail_sala@example.com")
    sala = _create_sala(client, nombre="Sala Disponibilidad")

    client.cookies.clear()
    _register_client_user(client, email="cliente_avail_sala@example.com")

    fecha = _future_date()

    booking_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": fecha,
            "hora_inicio": "09:00:00",
            "num_bloques": 2,
            "motivo": "Reunion de prueba",
        },
    )
    assert booking_response.status_code == 201

    availability_response = client.get(
        f"/api/resources/salas/{sala['id']}/availability", params={"fecha": fecha}
    )
    assert availability_response.status_code == 200
    blocks = availability_response.json()

    booked_block = next(b for b in blocks if b["hora_inicio"] == "09:00:00")
    assert booked_block["disponible"] is False

    free_block = next(b for b in blocks if b["hora_inicio"] == "11:00:00")
    assert free_block["disponible"] is True


def test_create_reserva_sala_success(client):
    _setup_admin(client, email="admin_create_sala@example.com")
    sala = _create_sala(client, nombre="Sala Crear")

    client.cookies.clear()
    _register_client_user(client, email="cliente_create_sala@example.com")

    response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "10:00:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "confirmada"
    assert body["hora_fin"] == "10:30:00"


def test_create_reserva_sala_misaligned_hora_inicio_rejected(client):
    _setup_admin(client, email="admin_misaligned@example.com")
    sala = _create_sala(client, nombre="Sala Misaligned")

    client.cookies.clear()
    _register_client_user(client, email="cliente_misaligned@example.com")

    response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:15:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )
    assert response.status_code == 422


def test_create_reserva_sala_outside_operating_hours_rejected(client):
    _setup_admin(client, email="admin_outofhours@example.com")
    sala = _create_sala(client, nombre="Sala OutOfHours")

    client.cookies.clear()
    _register_client_user(client, email="cliente_outofhours@example.com")

    response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "20:30:00",
            "num_bloques": 2,
            "motivo": "Reunion tardia",
        },
    )
    assert response.status_code == 422


def test_create_reserva_sala_past_date_rejected(client):
    _setup_admin(client, email="admin_pastdate@example.com")
    sala = _create_sala(client, nombre="Sala PastDate")

    client.cookies.clear()
    _register_client_user(client, email="cliente_pastdate@example.com")

    past_date = (date.today() - timedelta(days=1)).isoformat()

    response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": past_date,
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion pasada",
        },
    )
    assert response.status_code == 422


def test_create_reserva_sala_overlap_rejected(client):
    _setup_admin(client, email="admin_overlap_sala@example.com")
    sala = _create_sala(client, nombre="Sala Overlap")

    client.cookies.clear()
    _register_client_user(client, email="cliente_overlap_sala@example.com")

    fecha = _future_date()

    first = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 2, "motivo": "Primera"},
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:30:00", "num_bloques": 2, "motivo": "Segunda"},
    )
    assert second.status_code == 409


def test_create_reserva_sala_concurrent_only_one_succeeds(client, db_session):
    _setup_admin(client, email="admin_concurrent_sala@example.com")
    sala = _create_sala(client, nombre="Sala Concurrencia")
    sala_id = sala["id"]

    admin_me = client.get("/api/auth/me")
    user_id = admin_me.json()["id"]

    fecha_futura = date.today() + timedelta(days=14)

    barrier = threading.Barrier(2)
    results = []
    results_lock = threading.Lock()

    def attempt():
        session = TestSessionLocal()
        data = BookingCreateRequest(
            fecha=fecha_futura,
            hora_inicio=time(9, 0),
            num_bloques=2,
            motivo="Prueba de concurrencia",
        )
        barrier.wait()
        try:
            reserva = reserva_sala_service.create_reserva(
                session, sala_id=sala_id, user_id=user_id, data=data
            )
            with results_lock:
                results.append(("success", reserva.id))
        except reserva_sala_service.OverlapError:
            with results_lock:
                results.append(("conflict", None))
        finally:
            session.close()

    t1 = threading.Thread(target=attempt)
    t2 = threading.Thread(target=attempt)
    t1.start()
    t2.start()
    t1.join(timeout=15)
    t2.join(timeout=15)

    successes = [r for r in results if r[0] == "success"]
    conflicts = [r for r in results if r[0] == "conflict"]
    assert len(successes) == 1
    assert len(conflicts) == 1


def test_cancel_reserva_sala_by_owner_success(client):
    _setup_admin(client, email="admin_cancel_owner@example.com")
    sala = _create_sala(client, nombre="Sala CancelOwner")

    client.cookies.clear()
    _register_client_user(client, email="cliente_cancel_owner@example.com")

    fecha = _future_date()
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion"},
    )
    reserva_id = create_response.json()["id"]

    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["estado"] == "cancelada"


def test_cancel_reserva_sala_by_admin_success(client):
    _setup_admin(client, email="admin_cancel_admin@example.com")
    sala = _create_sala(client, nombre="Sala CancelAdmin")

    client.cookies.clear()
    _register_client_user(client, email="cliente_cancel_admin@example.com")

    fecha = _future_date()
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion"},
    )
    reserva_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "admin_cancel_admin@example.com")

    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["estado"] == "cancelada"


def test_cancel_reserva_sala_by_other_user_forbidden(client):
    _setup_admin(client, email="admin_cancel_forbidden@example.com")
    sala = _create_sala(client, nombre="Sala CancelForbidden")

    client.cookies.clear()
    _register_client_user(client, email="cliente_owner_cancel@example.com")

    fecha = _future_date()
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion"},
    )
    reserva_id = create_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_intruso_cancel@example.com")

    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 403


def test_cancel_reserva_sala_is_idempotent(client):
    _setup_admin(client, email="admin_cancel_idempotent@example.com")
    sala = _create_sala(client, nombre="Sala CancelIdempotent")

    client.cookies.clear()
    _register_client_user(client, email="cliente_cancel_idempotent@example.com")

    fecha = _future_date()
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion"},
    )
    reserva_id = create_response.json()["id"]

    first = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    second = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["estado"] == "cancelada"
    assert second.json()["estado"] == "cancelada"


def test_list_my_reservas_salas_returns_only_own(client):
    _setup_admin(client, email="admin_list_mine@example.com")
    sala = _create_sala(client, nombre="Sala ListMine")

    client.cookies.clear()
    _register_client_user(client, email="cliente_uno_list@example.com")

    fecha = _future_date()
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion Uno"},
    )

    client.cookies.clear()
    _register_client_user(client, email="cliente_dos_list@example.com")

    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reunion Dos"},
    )

    response = client.get("/api/resources/salas/reservas/me")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["motivo"] == "Reunion Dos"