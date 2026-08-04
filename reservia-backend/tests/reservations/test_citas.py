from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_citas@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Citas"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email="cliente_citas@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Citas"},
    )
    return _login_as(client, email)


def _create_provider_as_admin(client, email):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": "Proveedor Citas"},
    )


def _next_monday():
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).isoformat()


def test_provider_availability_respects_schedule_blocks(client):
    _setup_admin(client, email="admin_cita_avail@example.com")
    _create_provider_as_admin(client, email="provider_avail_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_avail_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "14:00:00", "end_time": "17:00:00"},
    )

    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    fecha_monday = _next_monday()

    client.cookies.clear()
    _login_as(client, "admin_cita_avail@example.com")

    availability_response = client.get(
        f"/api/providers/{provider_profile_id}/availability", params={"fecha": fecha_monday}
    )
    assert availability_response.status_code == 200
    blocks = availability_response.json()

    horas_inicio = [b["hora_inicio"] for b in blocks]
    assert "12:00:00" not in horas_inicio
    assert "13:00:00" not in horas_inicio
    assert "09:00:00" in horas_inicio
    assert "14:00:00" in horas_inicio


def test_create_cita_success(client):
    _setup_admin(client, email="admin_cita_create@example.com")
    _create_provider_as_admin(client, email="provider_create_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_create_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_cita_create@example.com")

    fecha_monday = _next_monday()

    response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Consulta",
        },
    )
    assert response.status_code == 201
    assert response.json()["estado"] == "confirmada"


def test_create_cita_outside_provider_schedule_rejected(client):
    _setup_admin(client, email="admin_cita_outside@example.com")
    _create_provider_as_admin(client, email="provider_outside_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_outside_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "14:00:00", "end_time": "17:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_cita_outside@example.com")

    fecha_monday = _next_monday()

    response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "12:30:00",
            "num_bloques": 1,
            "motivo": "Consulta almuerzo",
        },
    )
    assert response.status_code == 422


def test_create_cita_overlap_rejected(client):
    _setup_admin(client, email="admin_cita_overlap@example.com")
    _create_provider_as_admin(client, email="provider_overlap_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_overlap_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_cita_overlap@example.com")

    fecha_monday = _next_monday()

    first = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "09:00:00",
            "num_bloques": 2,
            "motivo": "Primera consulta",
        },
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "09:30:00",
            "num_bloques": 2,
            "motivo": "Segunda consulta",
        },
    )
    assert second.status_code == 409


def test_cancel_cita_by_provider_owner_success(client):
    _setup_admin(client, email="admin_cita_cancel@example.com")
    _create_provider_as_admin(client, email="provider_cancel_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_cancel_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_cita_cancel@example.com")

    fecha_monday = _next_monday()

    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Consulta",
        },
    )
    cita_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "provider_cancel_cita@example.com")

    cancel_response = client.patch(f"/api/providers/citas/{cita_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["estado"] == "cancelada"


def test_cancel_cita_by_other_provider_forbidden(client):
    _setup_admin(client, email="admin_cita_forbidden@example.com")
    _create_provider_as_admin(client, email="provider_owner_cita@example.com")
    _create_provider_as_admin(client, email="provider_intruder_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_owner_cita@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, email="cliente_cita_forbidden@example.com")

    fecha_monday = _next_monday()

    create_response = client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={
            "fecha": fecha_monday,
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Consulta",
        },
    )
    cita_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "provider_intruder_cita@example.com")

    cancel_response = client.patch(f"/api/providers/citas/{cita_id}/cancel")
    assert cancel_response.status_code == 403