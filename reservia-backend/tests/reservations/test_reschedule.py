from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_reschedule@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reschedule"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente Reschedule"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_sala(client, nombre="Sala Reschedule"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _create_provider_as_admin(client, email, full_name="Proveedor Reschedule"):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )


def _future_date(days=7):
    return (date.today() + timedelta(days=days)).isoformat()


def _next_monday():
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def test_reschedule_reserva_sala_success(client):
    _setup_admin(client, email="admin_resched_success@example.com")
    sala = _create_sala(client, "Sala Resched Success")

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_success@example.com")

    fecha_original = _future_date(7)
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_original, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Original"},
    )
    reserva_id = create_response.json()["id"]

    fecha_nueva = _future_date(10)
    reschedule_response = client.patch(
        f"/api/resources/salas/reservas/{reserva_id}/reschedule",
        json={"fecha": fecha_nueva, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reprogramada"},
    )
    assert reschedule_response.status_code == 200
    nueva_body = reschedule_response.json()
    assert nueva_body["estado"] == "confirmada"
    assert nueva_body["fecha"] == fecha_nueva
    assert nueva_body["hora_inicio"] == "11:00:00"

    original_response = client.get("/api/resources/salas/reservas/me")
    items = original_response.json()["items"]
    original_item = next(i for i in items if i["id"] == reserva_id)
    assert original_item["estado"] == "cancelada"


def test_reschedule_fails_when_new_slot_unavailable_old_stays_cancelled(client):
    _setup_admin(client, email="admin_resched_conflict@example.com")
    sala = _create_sala(client, "Sala Resched Conflict")

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_conflict_a@example.com", "Cliente Conflict A")

    fecha_original = _future_date(7)
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_original, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Original"},
    )
    reserva_id = create_response.json()["id"]

    fecha_destino = _future_date(10)

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_conflict_b@example.com", "Cliente Conflict B")

    ocupante_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_destino, "hora_inicio": "14:00:00", "num_bloques": 1, "motivo": "Ocupante"},
    )
    assert ocupante_response.status_code == 201

    client.cookies.clear()
    _login_as(client, "cliente_resched_conflict_a@example.com")

    reschedule_response = client.patch(
        f"/api/resources/salas/reservas/{reserva_id}/reschedule",
        json={"fecha": fecha_destino, "hora_inicio": "14:00:00", "num_bloques": 1, "motivo": "Intento"},
    )
    assert reschedule_response.status_code == 409

    check_response = client.get("/api/resources/salas/reservas/me")
    items = check_response.json()["items"]
    original_item = next(i for i in items if i["id"] == reserva_id)
    assert original_item["estado"] == "cancelada"


def test_reschedule_by_admin_success(client):
    _setup_admin(client, email="admin_resched_admin@example.com")
    sala = _create_sala(client, "Sala Resched Admin")

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_admin@example.com", "Cliente Dueno Original")

    fecha_original = _future_date(7)
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_original, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Original"},
    )
    reserva_id = create_response.json()["id"]
    original_user_id = create_response.json()["user_id"]

    client.cookies.clear()
    _login_as(client, "admin_resched_admin@example.com")

    fecha_nueva = _future_date(10)
    reschedule_response = client.patch(
        f"/api/resources/salas/reservas/{reserva_id}/reschedule",
        json={"fecha": fecha_nueva, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reprogramada por admin"},
    )
    assert reschedule_response.status_code == 200
    assert reschedule_response.json()["user_id"] == original_user_id


def test_reschedule_forbidden_for_non_owner_non_admin(client):
    _setup_admin(client, email="admin_resched_forbidden@example.com")
    sala = _create_sala(client, "Sala Resched Forbidden")

    client.cookies.clear()
    _register_client_user(client, "cliente_owner_resched@example.com")

    fecha_original = _future_date(7)
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_original, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Original"},
    )
    reserva_id = create_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_intruso_resched@example.com")

    reschedule_response = client.patch(
        f"/api/resources/salas/reservas/{reserva_id}/reschedule",
        json={"fecha": _future_date(10), "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Intento"},
    )
    assert reschedule_response.status_code == 403


def test_reschedule_already_cancelled_reserva_rejected(client):
    _setup_admin(client, email="admin_resched_cancelled@example.com")
    sala = _create_sala(client, "Sala Resched Cancelled")

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_cancelled@example.com")

    fecha_original = _future_date(7)
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha_original, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Original"},
    )
    reserva_id = create_response.json()["id"]

    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 200

    reschedule_response = client.patch(
        f"/api/resources/salas/reservas/{reserva_id}/reschedule",
        json={"fecha": _future_date(10), "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Intento"},
    )
    assert reschedule_response.status_code == 409


def test_reschedule_cita_success(client):
    _setup_admin(client, email="admin_resched_cita@example.com")
    _create_provider_as_admin(client, "provider_resched_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_resched_cita@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "17:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_cita@example.com")

    fecha_monday = _next_monday().isoformat()
    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta original"},
    )
    cita_id = create_response.json()["id"]

    reschedule_response = client.patch(
        f"/api/providers/citas/{cita_id}/reschedule",
        json={"fecha": fecha_monday, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Consulta reprogramada"},
    )
    assert reschedule_response.status_code == 200
    body = reschedule_response.json()
    assert body["estado"] == "confirmada"
    assert body["hora_inicio"] == "11:00:00"


def test_reschedule_cita_by_provider_owner_success(client):
    _setup_admin(client, email="admin_resched_cita_provider@example.com")
    _create_provider_as_admin(client, "provider_resched_cita_owner@example.com")

    client.cookies.clear()
    _login_as(client, "provider_resched_cita_owner@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "17:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_resched_cita_provider@example.com")

    fecha_monday = _next_monday().isoformat()
    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta original"},
    )
    cita_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "provider_resched_cita_owner@example.com")

    reschedule_response = client.patch(
        f"/api/providers/citas/{cita_id}/reschedule",
        json={"fecha": fecha_monday, "hora_inicio": "13:00:00", "num_bloques": 1, "motivo": "Reprogramada por proveedor"},
    )
    assert reschedule_response.status_code == 200
    assert reschedule_response.json()["hora_inicio"] == "13:00:00"


def test_reschedule_cita_forbidden_for_unrelated_user(client):
    _setup_admin(client, email="admin_resched_cita_forbidden@example.com")
    _create_provider_as_admin(client, "provider_resched_cita_forbidden@example.com")

    client.cookies.clear()
    _login_as(client, "provider_resched_cita_forbidden@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "17:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_owner_resched_cita@example.com")

    fecha_monday = _next_monday().isoformat()
    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta"},
    )
    cita_id = create_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_intruso_resched_cita@example.com")

    reschedule_response = client.patch(
        f"/api/providers/citas/{cita_id}/reschedule",
        json={"fecha": fecha_monday, "hora_inicio": "13:00:00", "num_bloques": 1, "motivo": "Intento"},
    )
    assert reschedule_response.status_code == 403