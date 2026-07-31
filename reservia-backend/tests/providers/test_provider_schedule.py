from app.core import config


def _setup_admin(client, email="admin_schedule@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Schedule"},
    )
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": "Secret123"}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return client


def _create_provider_as_admin(client, email):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": "Proveedor Schedule"},
    )


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def test_provider_adds_schedule_block_success(client):
    _setup_admin(client, email="admin_add_block@example.com")
    _create_provider_as_admin(client, email="provider_add_block@example.com")

    client.cookies.clear()
    _login_as(client, "provider_add_block@example.com")

    response = client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "monday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["day_of_week"] == "monday"
    assert body["estado"] == "active"


def test_provider_overlapping_schedule_block_rejected(client):
    _setup_admin(client, email="admin_overlap@example.com")
    _create_provider_as_admin(client, email="provider_overlap@example.com")

    client.cookies.clear()
    _login_as(client, "provider_overlap@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "tuesday", "start_time": "09:00:00", "end_time": "12:00:00"},
    )

    response = client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "tuesday", "start_time": "10:00:00", "end_time": "13:00:00"},
    )
    assert response.status_code == 409


def test_provider_cannot_deactivate_other_providers_schedule_block(client):
    _setup_admin(client, email="admin_other_block@example.com")
    _create_provider_as_admin(client, email="provider_owner@example.com")
    _create_provider_as_admin(client, email="provider_intruder@example.com")

    client.cookies.clear()
    _login_as(client, "provider_owner@example.com")

    create_response = client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "wednesday", "start_time": "08:00:00", "end_time": "10:00:00"},
    )
    block_id = create_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "provider_intruder@example.com")

    response = client.patch(f"/api/providers/me/schedule/{block_id}/deactivate")
    assert response.status_code == 403


def test_public_schedule_endpoint_only_shows_active_blocks(client):
    _setup_admin(client, email="admin_public_schedule@example.com")
    _create_provider_as_admin(client, email="provider_public@example.com")

    client.cookies.clear()
    _login_as(client, "provider_public@example.com")

    client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "thursday", "start_time": "09:00:00", "end_time": "11:00:00"},
    )
    second_block = client.post(
        "/api/providers/me/schedule",
        json={"day_of_week": "friday", "start_time": "09:00:00", "end_time": "11:00:00"},
    )

    second_block_id = second_block.json()["id"]
    client.patch(f"/api/providers/me/schedule/{second_block_id}/deactivate")

    profile_response = client.get("/api/providers/me/profile")
    provider_profile_id = profile_response.json()["id"]

    client.cookies.clear()
    _login_as(client, "admin_public_schedule@example.com")

    public_response = client.get(f"/api/providers/{provider_profile_id}/schedule")
    assert public_response.status_code == 200
    days = [block["day_of_week"] for block in public_response.json()]
    assert "thursday" in days
    assert "friday" not in days