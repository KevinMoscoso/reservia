from datetime import date, timedelta

from app.core import config


def _setup_admin(client, email="admin_reports@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reports"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _register_client_user(client, email, full_name="Cliente Reports"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )
    return _login_as(client, email)


def _create_sala(client, nombre="Sala Reports"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _create_provider_as_admin(client, email, full_name="Proveedor Reports"):
    return client.post(
        "/api/admin/providers",
        json={"email": email, "password": "Secret123", "full_name": full_name},
    )


def test_occupancy_report_admin_only(client):
    _register_client_user(client, "cliente_occ_forbidden@example.com")

    response = client.get("/api/reports/occupancy")
    assert response.status_code == 403


def test_occupancy_report_returns_correct_counts(client):
    _setup_admin(client, email="admin_occ_counts@example.com")
    sala = _create_sala(client, "Sala Occupancy Counts")

    client.cookies.clear()
    _register_client_user(client, "cliente_occ_counts@example.com")

    fecha = date.today().isoformat()
    booking_response = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 2, "motivo": "Reunion"},
    )
    assert booking_response.status_code == 201

    client.cookies.clear()
    _login_as(client, "admin_occ_counts@example.com")

    response = client.get(
        "/api/reports/occupancy", params={"fecha_inicio": fecha, "fecha_fin": fecha}
    )
    assert response.status_code == 200
    body = response.json()

    sala_item = next(
        item for item in body["items"]
        if item["resource_type"] == "sala" and item["resource_id"] == sala["id"]
    )
    assert sala_item["reservas_confirmadas"] == 1
    assert sala_item["bloques_reservados"] == 2


def test_occupancy_report_csv_returns_csv_content_type(client):
    _setup_admin(client, email="admin_occ_csv@example.com")
    _create_sala(client, "Sala Occupancy CSV")

    response = client.get("/api/reports/occupancy", params={"format": "csv"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")


def test_provider_activity_report_admin_sees_all_providers(client):
    _setup_admin(client, email="admin_prov_all@example.com")
    _create_provider_as_admin(client, "provider_all_one@example.com", "Proveedor Uno Reports")
    _create_provider_as_admin(client, "provider_all_two@example.com", "Proveedor Dos Reports")

    response = client.get("/api/reports/providers")
    assert response.status_code == 200
    body = response.json()

    nombres = {item["provider_full_name"] for item in body["items"]}
    assert "Proveedor Uno Reports" in nombres
    assert "Proveedor Dos Reports" in nombres


def test_provider_activity_report_provider_sees_only_own(client):
    _setup_admin(client, email="admin_prov_own@example.com")
    _create_provider_as_admin(client, "provider_own_self@example.com", "Proveedor Propio Reports")
    _create_provider_as_admin(client, "provider_own_other@example.com", "Proveedor Otro Reports")

    client.cookies.clear()
    _login_as(client, "provider_own_self@example.com")

    response = client.get("/api/reports/providers")
    assert response.status_code == 200
    body = response.json()

    assert len(body["items"]) == 1
    assert body["items"][0]["provider_full_name"] == "Proveedor Propio Reports"


def test_provider_activity_report_client_forbidden(client):
    _register_client_user(client, "cliente_prov_forbidden@example.com")

    response = client.get("/api/reports/providers")
    assert response.status_code == 403


def test_system_activity_report_admin_only(client):
    _setup_admin(client, email="admin_sys_only@example.com")
    _create_provider_as_admin(client, "provider_sys_forbidden@example.com")

    client.cookies.clear()
    _login_as(client, "provider_sys_forbidden@example.com")

    response = client.get("/api/reports/system")
    assert response.status_code == 403


def test_system_activity_report_returns_correct_counts(client):
    _setup_admin(client, email="admin_sys_counts@example.com")
    sala = _create_sala(client, "Sala System Counts")

    client.cookies.clear()
    _register_client_user(client, "cliente_sys_counts@example.com")

    fecha = (date.today() + timedelta(days=1)).isoformat()
    r1 = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "09:00:00", "num_bloques": 1, "motivo": "Reunion Uno"},
    )
    r2 = client.post(
        f"/api/resources/salas/{sala['id']}/reservas",
        json={"fecha": fecha, "hora_inicio": "11:00:00", "num_bloques": 1, "motivo": "Reunion Dos"},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201

    reserva_id_uno = r1.json()["id"]
    cancel_response = client.patch(f"/api/resources/salas/reservas/{reserva_id_uno}/cancel")
    assert cancel_response.status_code == 200

    client.cookies.clear()
    _login_as(client, "admin_sys_counts@example.com")

    response = client.get("/api/reports/system")
    assert response.status_code == 200
    body = response.json()

    assert body["total_general"] == 2
    assert body["total_cancelaciones"] == 1
    assert body["porcentaje_cancelacion"] == 50.0
    assert body["usuarios_activos"] == 1


def test_reports_default_date_range_when_not_specified(client):
    _setup_admin(client, email="admin_default_range@example.com")

    response = client.get("/api/reports/occupancy")
    assert response.status_code == 200
    body = response.json()

    expected_fecha_fin = date.today().isoformat()
    expected_fecha_inicio = (date.today() - timedelta(days=30)).isoformat()

    assert body["fecha_fin"] == expected_fecha_fin
    assert body["fecha_inicio"] == expected_fecha_inicio