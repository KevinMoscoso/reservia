from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_reservas_view@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reservas View"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_sala(client, nombre):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _create_equipo(client, codigo):
    response = client.post(
        "/api/resources/equipos/",
        json={"nombre": "Equipo Admin View", "codigo": codigo, "categoria": "AV"},
    )
    return response.json()


def _create_provider_as_admin(client, email):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": "Proveedor Admin View"},
    )


def _future_date():
    return (date.today() + timedelta(days=7)).isoformat()


def _next_monday():
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).isoformat()


def test_admin_lists_all_reservas_salas(client):
    _setup_admin(client, email="admin_list_salas_view@example.com")
    sala = _create_sala(client, "Sala Admin View")

    client.cookies.clear()
    _register_client_user(client, "cliente_uno_admin_view@example.com", "Cliente Uno View")
    fecha = _future_date()
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion Uno"},
    )

    client.cookies.clear()
    _register_client_user(client, "cliente_dos_admin_view@example.com", "Cliente Dos View")
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reunion Dos"},
    )

    client.cookies.clear()
    _login_as(client, "admin_list_salas_view@example.com")

    response = client.get("/api/resources/salas/reservas")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2

    nombres_sala = {item["sala_nombre"] for item in body}
    assert nombres_sala == {"Sala Admin View"}

    usuarios = {item["user_full_name"] for item in body}
    assert usuarios == {"Cliente Uno View", "Cliente Dos View"}


def test_admin_can_cancel_any_reserva_sala(client):
    _setup_admin(client, email="admin_cancel_any_sala@example.com")
    sala = _create_sala(client, "Sala Cancel Any")

    client.cookies.clear()
    _register_client_user(client, "cliente_cancel_any_sala@example.com", "Cliente Cancel Any")
    fecha = _future_date()
    create_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion"},
    )
    reserva_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "admin_cancel_any_sala@example.com")

    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["estado"] == "cancelada"

    list_response = client.get("/api/resources/salas/reservas")
    assert list_response.status_code == 200
    item = next(i for i in list_response.json() if i["id"] == reserva_id)
    assert item["estado"] == "cancelada"


def test_non_admin_forbidden_from_listing_all_reservas_salas(client):
    _register_client_user(client, "cliente_forbidden_list_salas@example.com", "Cliente Forbidden")

    response = client.get("/api/resources/salas/reservas")
    assert response.status_code == 403


def test_admin_lists_all_reservas_equipos(client):
    _setup_admin(client, email="admin_list_equipos_view@example.com")
    equipo = _create_equipo(client, "EQ-ADMIN-VIEW-001")

    client.cookies.clear()
    _register_client_user(client, "cliente_equipo_admin_view@example.com", "Cliente Equipo View")
    fecha = _future_date()
    client.post(
        f"/api/resources/equipos/{equipo['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Prestamo"},
    )

    client.cookies.clear()
    _login_as(client, "admin_list_equipos_view@example.com")

    response = client.get("/api/resources/equipos/reservas")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["equipo_nombre"] == "Equipo Admin View"
    assert body[0]["user_full_name"] == "Cliente Equipo View"


def test_admin_lists_all_citas(client):
    _setup_admin(client, email="admin_list_citas_view@example.com")
    _create_provider_as_admin(client, "provider_admin_view@example.com")

    client.cookies.clear()
    _login_as(client, "provider_admin_view@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_cita_admin_view@example.com", "Cliente Cita View")
    fecha_monday = _next_monday()
    client.post(
        f"/api/providers/{provider_profile_id}/citas",
        json={"fecha": fecha_monday, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Consulta"},
    )

    client.cookies.clear()
    _login_as(client, "admin_list_citas_view@example.com")

    response = client.get("/api/providers/citas")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["provider_full_name"] == "Proveedor Admin View"
    assert body[0]["user_full_name"] == "Cliente Cita View"


def test_non_admin_forbidden_from_listing_all_citas(client):
    _register_client_user(client, "cliente_forbidden_list_citas@example.com", "Cliente Forbidden Citas")

    response = client.get("/api/providers/citas")
    assert response.status_code == 403