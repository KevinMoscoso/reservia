from app.core import config


def _create_admin_client(client, email="admin_equipos@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Equipos"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def _create_client_user(client, email="cliente_equipos@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Equipos"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def test_create_equipo_as_admin_success(client):
    _create_admin_client(client)
    response = client.post(
        "/api/resources/equipos/",
        json={"nombre": "Proyector", "codigo": "EQ-001", "categoria": "AV"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["codigo"] == "EQ-001"
    assert body["estado"] == "active"


def test_create_equipo_duplicate_codigo_rejected(client):
    _create_admin_client(client, email="admin_dup@example.com")
    client.post(
        "/api/resources/equipos/",
        json={"nombre": "Laptop", "codigo": "EQ-DUP", "categoria": "Computo"},
    )
    response = client.post(
        "/api/resources/equipos/",
        json={"nombre": "Laptop 2", "codigo": "EQ-DUP", "categoria": "Computo"},
    )
    assert response.status_code == 409


def test_create_equipo_as_non_admin_forbidden(client):
    _create_client_user(client)
    response = client.post(
        "/api/resources/equipos/",
        json={"nombre": "Camara", "codigo": "EQ-002", "categoria": "AV"},
    )
    assert response.status_code == 403