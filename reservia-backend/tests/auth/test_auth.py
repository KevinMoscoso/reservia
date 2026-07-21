from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core import config
from app.core.database import SessionLocal, engine, get_db
from app.main import app
from app.models.auth.session import Session as SessionModel
from app.models.auth.user import User
from app.models.shared.audit_log import AuditLog
from app.models.shared.base import Base


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def _clean_tables(db_session):
    yield
    db_session.query(SessionModel).delete()
    db_session.query(AuditLog).delete()
    db_session.query(User).delete()
    db_session.commit()


@pytest.fixture()
def client():
    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register_client(client, email="client@example.com", password="Secret123"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Cliente Uno"},
    )


def _setup_admin(client, email="admin@example.com", password="Secret123"):
    return client.post(
        "/api/auth/setup",
        json={"email": email, "password": password, "full_name": "Admin Uno"},
    )


def test_register_client_success(client):
    response = _register_client(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "client@example.com"
    assert body["role"] == "client"
    assert "password_hash" not in body


def test_register_duplicate_email_rejected(client):
    _register_client(client)
    response = _register_client(client)
    assert response.status_code == 409


def test_register_concurrent_duplicate_email_only_one_succeeds(client, db_session):
    from unittest.mock import patch

    from app.repositories.auth import user_repository
    from app.schemas.auth.user import RegisterClientRequest
    from app.services.auth import auth_service

    data = RegisterClientRequest(
        email="race@example.com", password="Secret123", full_name="Race Condition"
    )

    session_a = SessionLocal()
    session_b = SessionLocal()

    # Primera "solicitud": se registra y confirma normalmente
    auth_service.register_client(session_a, data)

    # Segunda "solicitud": simula que su chequeo de pre-existencia ya había
    # pasado (ventana de carrera) antes de que la primera insercion fuera
    # visible. Esto obliga a llegar al INSERT real y disparar el
    # IntegrityError que auth_service.register_client debe capturar.
    with patch.object(user_repository, "get_by_email", return_value=None):
        with pytest.raises(auth_service.EmailAlreadyRegisteredError):
            auth_service.register_client(session_b, data)

    session_a.close()
    session_b.close()


def test_register_weak_password_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "weak@example.com", "password": "1234567", "full_name": "Debil"},
    )
    assert response.status_code == 422


def test_login_success_sets_session(client):
    _register_client(client, email="login@example.com", password="Secret123")
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "Secret123"},
    )
    assert response.status_code == 200
    assert config.SESSION_COOKIE_NAME in response.cookies


def test_login_nonexistent_email_generic_error(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "noexiste@example.com", "password": "Secret123"},
    )
    assert response.status_code == 401


def test_login_lockout_after_max_failed_attempts(client):
    _register_client(client, email="lockout@example.com", password="Secret123")

    for _ in range(config.LOGIN_MAX_ATTEMPTS):
        client.post(
            "/api/auth/login",
            json={"email": "lockout@example.com", "password": "wrongpass1"},
        )

    response = client.post(
        "/api/auth/login",
        json={"email": "lockout@example.com", "password": "Secret123"},
    )
    assert response.status_code == 423


def test_protected_endpoint_without_session_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_protected_endpoint_expired_by_inactivity_401(client, db_session):
    _register_client(client, email="expired@example.com", password="Secret123")
    login_response = client.post(
        "/api/auth/login",
        json={"email": "expired@example.com", "password": "Secret123"},
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]

    session = db_session.query(SessionModel).filter(SessionModel.id == token).first()
    session.last_seen_at = datetime.utcnow() - timedelta(
        minutes=config.SESSION_INACTIVITY_TIMEOUT_MINUTES + 1
    )
    db_session.add(session)
    db_session.commit()

    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_client_forbidden_from_admin_endpoint(client):
    _register_client(client, email="normal@example.com", password="Secret123")
    login_response = client.post(
        "/api/auth/login",
        json={"email": "normal@example.com", "password": "Secret123"},
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)

    response = client.post(
        "/api/admin/providers",
        json={
            "email": "provider@example.com",
            "password": "Secret123",
            "full_name": "Proveedor Uno",
        },
    )
    assert response.status_code == 403


def test_setup_endpoint_blocked_after_first_admin(client):
    first = _setup_admin(client)
    assert first.status_code == 201

    second = _setup_admin(client, email="admin2@example.com")
    assert second.status_code == 403


def test_logout_invalidates_session(client):
    _register_client(client, email="logout@example.com", password="Secret123")
    login_response = client.post(
        "/api/auth/login",
        json={"email": "logout@example.com", "password": "Secret123"},
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 401


def test_sql_injection_attempt_in_email_field_is_safely_rejected(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "' OR '1'='1", "password": "whatever1"},
    )
    assert response.status_code in (401, 422)