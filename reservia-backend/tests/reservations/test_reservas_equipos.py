from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_reservas_equipos@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reservas Equipos"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email="cliente_reservas_equipos@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Reservas Equipos"},
    )
    return _login_as(client, email)


def _create_equipo(client, codigo="EQ-RES-001"):
    response = client.post(
        "/api/resources/equipos/",
        json={"nombre": "Proyector Reservable", "codigo": codigo, "categoria": "AV"},
    )
    return response.json()


def _future_date():
    return (date.today() + timedelta(days=7)).isoformat()


def test_create_reserva_equipo_success(client):
    _setup_admin(client, email="admin_equipo_create@example.com")
    equipo = _create_equipo(client, codigo="EQ-CREATE-001")

    client.cookies.clear()
    _register_client_user(client, email="cliente_equipo_create@example.com")

    response = client.post(
        f"/api/resources/equipos/{equipo['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "10:00:00",
            "num_bloques": 1,
            "motivo": "Prestamo de equipo",
        },
    )
    assert response.status_code == 201
    assert response.json()["estado"] == "confirmada"


def test_create_reserva_equipo_overlap_rejected(client):
    _setup_admin(client, email="admin_equipo_overlap@example.com")
    equipo = _create_equipo(client, codigo="EQ-OVERLAP-001")

    client.cookies.clear()
    _register_client_user(client, email="cliente_equipo_overlap@example.com")

    fecha = _future_date()

    first = client.post(
        f"/api/resources/equipos/{equipo['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 2, "motivo": "Primera"},
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/resources/equipos/{equipo['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:30:00", "num_bloques": 2, "motivo": "Segunda"},
    )
    assert second.status_code == 409


def test_cancel_reserva_equipo_by_owner_success(client):
    _setup_admin(client, email="admin_equipo_cancel@example.com")
    equipo = _create_equipo(client, codigo="EQ-CANCEL-001")

    client.cookies.clear()
    _register_client_user(client, email="cliente_equipo_cancel@example.com")

    create_response = client.post(
        f"/api/resources/equipos/{equipo['id']}/reservas",
        json={
            "fecha": _future_date(),
            "hora_inicio": "10:00:00",
            "num_bloques": 1,
            "motivo": "Prestamo",
        },
    )
    reserva_id = create_response.json()["id"]

    cancel_response = client.patch(f"/api/resources/equipos/reservas/{reserva_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["estado"] == "cancelada"