from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_audit@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Audit"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente Audit"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )


def test_audit_log_admin_only(client):
    _register_client_user(client, "cliente_audit_forbidden@example.com")
    _login_as(client, "cliente_audit_forbidden@example.com")

    response = client.get("/api/audit/")
    assert response.status_code == 403


def test_audit_log_returns_paginated_results(client):
    _setup_admin(client, email="admin_audit_pagination@example.com")

    _register_client_user(client, "cliente_audit_page_uno@example.com", "Cliente Page Uno")
    _register_client_user(client, "cliente_audit_page_dos@example.com", "Cliente Page Dos")

    today = date.today().isoformat()

    response_page1 = client.get(
        "/api/audit/",
        params={"fecha_inicio": today, "fecha_fin": today, "page": 1, "page_size": 2},
    )
    assert response_page1.status_code == 200
    body_page1 = response_page1.json()
    assert len(body_page1["items"]) == 2
    assert body_page1["total"] >= 3

    response_page2 = client.get(
        "/api/audit/",
        params={"fecha_inicio": today, "fecha_fin": today, "page": 2, "page_size": 2},
    )
    assert response_page2.status_code == 200
    body_page2 = response_page2.json()
    assert len(body_page2["items"]) >= 1


def test_audit_log_includes_actor_full_name(client):
    _setup_admin(client, email="admin_audit_actor@example.com")
    _register_client_user(client, "cliente_audit_actor@example.com", "Cliente Actor Nombre")

    today = date.today().isoformat()

    response = client.get(
        "/api/audit/", params={"fecha_inicio": today, "fecha_fin": today}
    )
    assert response.status_code == 200
    body = response.json()

    matching = [
        item for item in body["items"]
        if item["actor_full_name"] == "Cliente Actor Nombre"
    ]
    assert len(matching) >= 1


def test_audit_log_handles_null_actor(client):
    _setup_admin(client, email="admin_audit_null@example.com")

    failed_login = client.post(
        "/api/auth/login",
        json={"email": "noexiste_audit@example.com", "password": "whatever1"},
    )
    assert failed_login.status_code == 401

    today = date.today().isoformat()

    response = client.get(
        "/api/audit/", params={"fecha_inicio": today, "fecha_fin": today}
    )
    assert response.status_code == 200
    body = response.json()

    null_actor_items = [
        item for item in body["items"]
        if item["action"] == "user.login_failed" and item["actor_user_id"] is None
    ]
    assert len(null_actor_items) >= 1
    assert null_actor_items[0]["actor_full_name"] is None


def test_audit_log_empty_range_returns_no_items(client):
    _setup_admin(client, email="admin_audit_empty@example.com")

    future_start = (date.today() + timedelta(days=365)).isoformat()
    future_end = (date.today() + timedelta(days=366)).isoformat()

    response = client.get(
        "/api/audit/", params={"fecha_inicio": future_start, "fecha_fin": future_end}
    )
    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 0
    assert body["items"] == []