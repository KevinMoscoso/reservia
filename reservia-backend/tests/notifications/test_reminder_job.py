from datetime import datetime, timedelta

from app.core import config
from app.models.notifications.notificacion import Notificacion
from app.models.reservations.reserva_sala import EstadoReserva, ReservaSala
from app.services.notifications.reminder_job import check_and_send_reminders
from tests.conftest import TestSessionLocal


def _setup_admin(client, email="admin_reminder@example.com"):
    client.post(
        "/api/auth/setup",
        json={"email": email, "password": "Secret123", "full_name": "Admin Reminder"},
    )
    return _login_as(client, email)


def _login_as(client, email, password="Secret123"):
    login_response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    token = login_response.cookies[config.SESSION_COOKIE_NAME]
    client.cookies.set(config.SESSION_COOKIE_NAME, token)
    return login_response


def _create_sala(client, nombre="Sala Reminder"):
    response = client.post(
        "/api/resources/salas/",
        json={"nombre": nombre, "ubicacion": "Piso 1", "capacidad": 10},
    )
    return response.json()


def _register_client_user(client, email="cliente_reminder@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Secret123", "full_name": "Cliente Reminder"},
    )
    return _login_as(client, email)


def test_reminder_job_creates_notification_for_upcoming_reserva(client, db_session):
    _setup_admin(client, email="admin_reminder_upcoming@example.com")
    sala = _create_sala(client, "Sala Reminder Upcoming")

    client.cookies.clear()
    _register_client_user(client, "cliente_reminder_upcoming@example.com")
    user_id = client.get("/api/auth/me").json()["id"]

    now = datetime.now()
    upcoming_start = now + timedelta(minutes=30)

    reserva = ReservaSala(
        sala_id=sala["id"],
        user_id=user_id,
        fecha=upcoming_start.date(),
        hora_inicio=upcoming_start.time().replace(microsecond=0),
        hora_fin=(upcoming_start + timedelta(minutes=30)).time().replace(microsecond=0),
        motivo="Prueba de recordatorio",
        estado=EstadoReserva.confirmada,
        recordatorio_enviado=False,
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)

    check_and_send_reminders(session_factory=TestSessionLocal)

    db_session.commit()
    db_session.refresh(reserva)
    assert reserva.recordatorio_enviado is True

    notif = (
        db_session.query(Notificacion)
        .filter(Notificacion.user_id == user_id, Notificacion.entity_id == reserva.id)
        .first()
    )
    assert notif is not None
    assert notif.tipo.value == "recordatorio"


def test_reminder_job_does_not_duplicate_already_sent_reminder(client, db_session):
    _setup_admin(client, email="admin_reminder_dup@example.com")
    sala = _create_sala(client, "Sala Reminder Dup")

    client.cookies.clear()
    _register_client_user(client, "cliente_reminder_dup@example.com")
    user_id = client.get("/api/auth/me").json()["id"]

    now = datetime.now()
    upcoming_start = now + timedelta(minutes=30)

    reserva = ReservaSala(
        sala_id=sala["id"],
        user_id=user_id,
        fecha=upcoming_start.date(),
        hora_inicio=upcoming_start.time().replace(microsecond=0),
        hora_fin=(upcoming_start + timedelta(minutes=30)).time().replace(microsecond=0),
        motivo="Prueba de no duplicado",
        estado=EstadoReserva.confirmada,
        recordatorio_enviado=False,
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)

    check_and_send_reminders(session_factory=TestSessionLocal)
    check_and_send_reminders(session_factory=TestSessionLocal)

    db_session.commit()

    count = (
        db_session.query(Notificacion)
        .filter(Notificacion.user_id == user_id, Notificacion.entity_id == reserva.id)
        .count()
    )
    assert count == 1


def test_reminder_job_ignores_reservations_outside_threshold(client, db_session):
    _setup_admin(client, email="admin_reminder_outside@example.com")
    sala = _create_sala(client, "Sala Reminder Outside")

    client.cookies.clear()
    _register_client_user(client, "cliente_reminder_outside@example.com")
    user_id = client.get("/api/auth/me").json()["id"]

    now = datetime.now()
    far_start = now + timedelta(hours=config.REMINDER_HOURS_BEFORE + 5)

    reserva = ReservaSala(
        sala_id=sala["id"],
        user_id=user_id,
        fecha=far_start.date(),
        hora_inicio=far_start.time().replace(microsecond=0),
        hora_fin=(far_start + timedelta(minutes=30)).time().replace(microsecond=0),
        motivo="Prueba fuera de umbral",
        estado=EstadoReserva.confirmada,
        recordatorio_enviado=False,
    )
    db_session.add(reserva)
    db_session.commit()
    db_session.refresh(reserva)

    check_and_send_reminders(session_factory=TestSessionLocal)

    db_session.commit()
    db_session.refresh(reserva)
    assert reserva.recordatorio_enviado is False

    count = (
        db_session.query(Notificacion)
        .filter(Notificacion.user_id == user_id, Notificacion.entity_id == reserva.id)
        .count()
    )
    assert count == 0