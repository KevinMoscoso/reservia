from app.core import config


def _setup_admin(client, email="admin_providers@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Providers"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def _create_provider_as_admin(client, email="provider1@example.com"):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": "Proveedor Uno"},
    )


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _create_client_user(client, email="cliente_providers@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Providers"},
    )
    _login_as(client, email)


def test_provider_profile_auto_created_when_admin_creates_provider(client):
    _setup_admin(client)
    _create_provider_as_admin(client, email="provider_auto@example.com")

    client.cookies.clear()
    _login_as(client, "provider_auto@example.com")

    response = client.get("/api/providers/me/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["slot_duration_minutes"] == 30


def test_provider_updates_own_slot_duration_success(client):
    _setup_admin(client, email="admin_update_slot@example.com")
    _create_provider_as_admin(client, email="provider_update@example.com")

    client.cookies.clear()
    _login_as(client, "provider_update@example.com")

    response = client.put(
        "/api/providers/me/profile", json={"slot_duration_minutes": 45}
    )
    assert response.status_code == 200
    assert response.json()["slot_duration_minutes"] == 45


def test_provider_invalid_slot_duration_rejected(client):
    _setup_admin(client, email="admin_invalid_slot@example.com")
    _create_provider_as_admin(client, email="provider_invalid@example.com")

    client.cookies.clear()
    _login_as(client, "provider_invalid@example.com")

    response = client.put(
        "/api/providers/me/profile", json={"slot_duration_minutes": 0}
    )
    assert response.status_code == 422

    response_high = client.put(
        "/api/providers/me/profile", json={"slot_duration_minutes": 1000}
    )
    assert response_high.status_code == 422


def test_client_cannot_access_provider_me_endpoints(client):
    _create_client_user(client, email="cliente_forbidden@example.com")

    response = client.get("/api/providers/me/profile")
    assert response.status_code == 403