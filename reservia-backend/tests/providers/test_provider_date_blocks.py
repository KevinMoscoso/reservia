from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_dateblocks@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin DateBlocks"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente DateBlocks"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_provider_as_admin(client, email, full_name="Proveedor DateBlocks"):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )


def _next_monday():
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def test_provider_creates_date_block_success(client):
    _setup_admin(client, email="admin_create_block@example.com")
    _create_provider_as_admin(client, "provider_create_block@example.com")

    client.cookies.clear()
    _login_as(client, "provider_create_block@example.com")

    fecha = _next_monday().isoformat()

    response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha, "motivo": "Vacaciones"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["fecha"] == fecha
    assert body["motivo"] == "Vacaciones"
    assert body["estado"] == "active"


def test_blocking_date_with_existing_citas_rejected(client):
    _setup_admin(client, email="admin_block_conflict@example.com")
    _create_provider_as_admin(client, "provider_block_conflict@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_conflict@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_block_conflict@example.com")

    fecha_monday = _next_monday().isoformat()
    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta"},
    )
    assert create_response.status_code == 201

    client.cookies.clear()
    _login_as(client, "provider_block_conflict@example.com")

    block_response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha_monday, "motivo": "Intento de bloqueo"},
    )
    assert block_response.status_code == 409


def test_blocking_past_date_rejected(client):
    _setup_admin(client, email="admin_block_pastdate@example.com")
    _create_provider_as_admin(client, "provider_block_pastdate@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_pastdate@example.com")

    past_date = (date.today() - timedelta(days=1)).isoformat()

    response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": past_date, "motivo": "Fecha pasada"},
    )
    assert response.status_code == 422


def test_availability_returns_empty_for_blocked_date(client):
    _setup_admin(client, email="admin_block_availability@example.com")
    _create_provider_as_admin(client, "provider_block_availability@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_availability@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    fecha_monday = _next_monday().isoformat()

    block_response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha_monday, "motivo": "Dia bloqueado"},
    )
    assert block_response.status_code == 201

    availability_response = client.get(
        f"/api/providers/{provider_profile_id}/availability", params={"fecha": fecha_monday}
    )
    assert availability_response.status_code == 200
    assert availability_response.json() == []


def test_create_cita_on_blocked_date_rejected(client):
    _setup_admin(client, email="admin_block_create_cita@example.com")
    _create_provider_as_admin(client, "provider_block_create_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_create_cita@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    fecha_monday = _next_monday().isoformat()

    block_response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha_monday, "motivo": "Dia bloqueado"},
    )
    assert block_response.status_code == 201

    client.cookies.clear()
    _register_client_user(client, "cliente_block_create_cita@example.com")

    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta"},
    )
    assert create_response.status_code == 422
    assert "no esta disponible" in create_response.json()["detail"]


def test_deactivate_date_block_is_idempotent(client):
    _setup_admin(client, email="admin_block_idempotent@example.com")
    _create_provider_as_admin(client, "provider_block_idempotent@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_idempotent@example.com")

    fecha = _next_monday().isoformat()
    create_response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha, "motivo": "Bloqueo idempotente"},
    )
    block_id = create_response.json()["id"]

    first = client.patch(f"/api/providers/me/date-blocks/{block_id}/deactivate")
    second = client.patch(f"/api/providers/me/date-blocks/{block_id}/deactivate")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["estado"] == "inactive"
    assert second.json()["estado"] == "inactive"


def test_provider_cannot_deactivate_other_providers_date_block(client):
    _setup_admin(client, email="admin_block_forbidden@example.com")
    _create_provider_as_admin(client, "provider_block_owner@example.com")
    _create_provider_as_admin(client, "provider_block_intruder@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_owner@example.com")

    fecha = _next_monday().isoformat()
    create_response = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha, "motivo": "Bloqueo del dueno"},
    )
    block_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "provider_block_intruder@example.com")

    response = client.patch(f"/api/providers/me/date-blocks/{block_id}/deactivate")
    assert response.status_code == 403


def test_list_own_date_blocks_includes_active_and_inactive(client):
    _setup_admin(client, email="admin_block_list@example.com")
    _create_provider_as_admin(client, "provider_block_list@example.com")

    client.cookies.clear()
    _login_as(client, "provider_block_list@example.com")

    fecha_uno = _next_monday().isoformat()
    fecha_dos = (_next_monday() + timedelta(days=7)).isoformat()

    create_uno = client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha_uno, "motivo": "Bloqueo activo"},
    )
    block_uno_id = create_uno.json()["id"]

    client.post(
        "/api/providers/me/date-blocks",
        json={"fecha": fecha_dos, "motivo": "Bloqueo a desactivar"},
    )

    client.patch(f"/api/providers/me/date-blocks/{block_uno_id}/deactivate")

    list_response = client.get("/api/providers/me/date-blocks")
    assert list_response.status_code == 200
    body = list_response.json()

    estados = {item["estado"] for item in body}
    assert "active" in estados
    assert "inactive" in estados