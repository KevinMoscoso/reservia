from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_notif@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Notif"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente Notif"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_sala(client, nombre="Sala Notif"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _create_provider_as_admin(client, email):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": "Proveedor Notif"},
    )


def _future_date():
    return (date.today() + timedelta(days=7)).isoformat()


def _next_monday():
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).isoformat()


def test_notification_created_on_reserva_sala_creation(client):
    _setup_admin(client, email="admin_notif_sala@example.com")
    sala = _create_sala(client, "Sala Notif Uno")

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_sala@example.com")

    booking_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )
    assert booking_response.status_code == 201

    notif_response = client.get("/api/notifications/me")
    assert notif_response.status_code == 200
    body = notif_response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["tipo"] == "reserva_confirmada"
    assert "Sala Notif Uno" in body["items"][0]["mensaje"]


def test_notification_created_on_cita_creation_for_both_client_and_provider(client):
    _setup_admin(client, email="admin_notif_cita@example.com")
    _create_provider_as_admin(client, "provider_notif_cita@example.com")

    client.cookies.clear()
    _login_as(client, "provider_notif_cita@example.com")
    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_cita@example.com")

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
    assert create_response.status_code == 201

    client_notif_response = client.get("/api/notifications/me")
    client_notifs = client_notif_response.json()["items"]
    assert len(client_notifs) == 1
    assert client_notifs[0]["tipo"] == "cita_confirmada"

    client.cookies.clear()
    _login_as(client, "provider_notif_cita@example.com")

    provider_notif_response = client.get("/api/notifications/me")
    provider_notifs = provider_notif_response.json()["items"]
    assert len(provider_notifs) == 1
    assert provider_notifs[0]["tipo"] == "cita_confirmada"


def test_list_my_notifications_returns_only_own(client):
    _setup_admin(client, email="admin_notif_own@example.com")
    sala = _create_sala(client, "Sala Notif Own")

    client.cookies.clear()
    _register_client_user(client, "cliente_uno_notif_own@example.com", "Cliente Uno Notif")
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion Uno",
        },
    )

    client.cookies.clear()
    _register_client_user(client, "cliente_dos_notif_own@example.com", "Cliente Dos Notif")
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "11:00:00",
            "num_bloques": 1,
            "motivo": "Reunion Dos",
        },
    )

    response = client.get("/api/notifications/me")
    body = response.json()["items"]
    assert len(body) == 1
    assert "Reunion Dos" not in str(body)


def test_unread_count_correct(client):
    _setup_admin(client, email="admin_notif_unread@example.com")
    sala = _create_sala(client, "Sala Notif Unread")

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_unread@example.com")

    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )

    response = client.get("/api/notifications/me/unread-count")
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_mark_notification_as_read(client):
    _setup_admin(client, email="admin_notif_read@example.com")
    sala = _create_sala(client, "Sala Notif Read")

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_read@example.com")

    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )

    list_response = client.get("/api/notifications/me")
    notif_id = list_response.json()["items"][0]["id"]

    read_response = client.patch(f"/api/notifications/{notif_id}/read")
    assert read_response.status_code == 200
    assert read_response.json()["leida"] is True

    unread_response = client.get("/api/notifications/me/unread-count")
    assert unread_response.json()["count"] == 0


def test_cannot_mark_other_users_notification_as_read(client):
    _setup_admin(client, email="admin_notif_forbidden@example.com")
    sala = _create_sala(client, "Sala Notif Forbidden")

    client.cookies.clear()
    _register_client_user(client, "cliente_owner_notif@example.com")

    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "09:00:00",
            "num_bloques": 1,
            "motivo": "Reunion",
        },
    )

    list_response = client.get("/api/notifications/me")
    notif_id = list_response.json()["items"][0]["id"]

    client.cookies.clear()
    _register_client_user(client, "cliente_intruso_notif@example.com")

    read_response = client.patch(f"/api/notifications/{notif_id}/read")
    assert read_response.status_code == 403


def test_mark_all_as_read(client):
    _setup_admin(client, email="admin_notif_all@example.com")
    sala = _create_sala(client, "Sala Notif All")

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_all@example.com")

    fecha = _future_date()
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion Uno"},
    )
    client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reunion Dos"},
    )

    mark_response = client.patch("/api/notifications/me/read-all")
    assert mark_response.status_code == 200
    assert mark_response.json() == {"detail": "ok"}

    unread_response = client.get("/api/notifications/me/unread-count")
    assert unread_response.json()["count"] == 0