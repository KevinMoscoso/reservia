from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_pagination@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Pagination"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente Pagination"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_sala(client, nombre="Sala Pagination"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def test_my_reservas_salas_pagination_returns_correct_page(client):
    _setup_admin(client, email="admin_my_reservas_page@example.com")
    sala = _create_sala(client, "Sala My Reservas Page")

    client.cookies.clear()
    _register_client_user(client, "cliente_my_reservas_page@example.com")

    fecha_uno = (date.today() + timedelta(days=1)).isoformat()
    fecha_dos = (date.today() + timedelta(days=2)).isoformat()
    fecha_tres = (date.today() + timedelta(days=3)).isoformat()

    for fecha in (fecha_uno, fecha_dos, fecha_tres):
        response = client.post(
            f"/api/resources/salas/{sala['id']}/reservas",
            json={
                "fecha": fecha,
                "hora_inicio": "09:00:00",
                "num_bloques": 1,
                "motivo": f"Reunion {fecha}",
            },
        )
        assert response.status_code == 201

    page1 = client.get(
        "/api/resources/salas/reservas/me", params={"page": 1, "page_size": 2}
    )
    assert page1.status_code == 200
    body1 = page1.json()
    assert len(body1["items"]) == 2
    assert body1["total"] == 3
    assert body1["total_pages"] == 2

    page2 = client.get(
        "/api/resources/salas/reservas/me", params={"page": 2, "page_size": 2}
    )
    assert page2.status_code == 200
    body2 = page2.json()
    assert len(body2["items"]) == 1


def test_notifications_pagination_returns_correct_page(client):
    _setup_admin(client, email="admin_notif_page@example.com")
    sala = _create_sala(client, "Sala Notif Page")

    client.cookies.clear()
    _register_client_user(client, "cliente_notif_page@example.com")

    fecha_uno = (date.today() + timedelta(days=1)).isoformat()
    fecha_dos = (date.today() + timedelta(days=2)).isoformat()
    fecha_tres = (date.today() + timedelta(days=3)).isoformat()

    for fecha in (fecha_uno, fecha_dos, fecha_tres):
        response = client.post(
            f"/api/resources/salas/{sala['id']}/reservas",
            json={
                "fecha": fecha,
                "hora_inicio": "09:00:00",
                "num_bloques": 1,
                "motivo": f"Reunion {fecha}",
            },
        )
        assert response.status_code == 201

    page1 = client.get("/api/notifications/me", params={"page": 1, "page_size": 2})
    assert page1.status_code == 200
    body1 = page1.json()
    assert len(body1["items"]) == 2
    assert body1["total"] >= 3

    page2 = client.get("/api/notifications/me", params={"page": 2, "page_size": 2})
    assert page2.status_code == 200
    body2 = page2.json()
    assert len(body2["items"]) >= 1