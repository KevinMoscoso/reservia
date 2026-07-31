from app.core import config


def _create_admin_client(client, email="admin_salas@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Salas"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def _create_client_user(client, email="cliente_salas@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Salas"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def test_create_sala_as_admin_success(client):
    _create_admin_client(client)
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": "Sala A", "ubicacion": "Piso 1", "capacidad": 10},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Sala A"
    assert body["estado"] == "active"


def test_create_sala_as_non_admin_forbidden(client):
    _create_client_user(client)
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": "Sala B", "ubicacion": "Piso 2", "capacidad": 5},
    )
    assert response.status_code == 403


def test_create_sala_invalid_capacidad_rejected(client):
    _create_admin_client(client, email="admin_cap@example.com")
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": "Sala C", "ubicacion": "Piso 3", "capacidad": 0},
    )
    assert response.status_code == 422


def test_list_salas_requires_authentication(client):
    response = client.get("/api/resources/salas/")
    assert response.status_code == 401


def test_update_sala_success(client):
    _create_admin_client(client, email="admin_update@example.com")
    create_response = client.post(
        "/api/resources/salas/",
        json={"nombre": "Sala D", "ubicacion": "Piso 4", "capacidad": 8},
    )
    sala_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/resources/salas/{sala_id}",
        json={"nombre": "Sala D Renovada"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["nombre"] == "Sala D Renovada"


def test_deactivate_sala_is_idempotent(client):
    _create_admin_client(client, email="admin_deact@example.com")
    create_response = client.post(
        "/api/resources/salas/",
        json={"nombre": "Sala E", "ubicacion": "Piso 5", "capacidad": 6},
    )
    sala_id = create_response.json()["id"]

    first = client.patch(f"/api/resources/salas/{sala_id}/deactivate")
    second = client.patch(f"/api/resources/salas/{sala_id}/deactivate")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["estado"] == "inactive"
    assert second.json()["estado"] == "inactive"