from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient

from app.core import config as app_config
from app.core.database import get_db
from app.main import app
from app.models.shared.base import Base
from app.models.auth.session import Session as SessionModel
from app.models.auth.user import User
from app.models.shared.audit_log import AuditLog
from app.models.resources.sala import Sala
from app.models.resources.equipo import Equipo
from app.models.providers.provider_profile import ProviderProfile
from app.models.providers.provider_schedule import ProviderSchedule
from app.models.reservations.reserva_sala import ReservaSala
from app.models.reservations.reserva_equipo import ReservaEquipo
from app.models.reservations.cita import Cita
from app.models.notifications.notificacion import Notificacion

TEST_SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{app_config.DB_USER}:{app_config.DB_PASSWORD}"
    f"@{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.TEST_DB_NAME}"
)
test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture()
def client():
    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _clean_all_tables(db_session):
    yield
    db_session.query(Notificacion).delete()
    db_session.query(Cita).delete()
    db_session.query(ReservaEquipo).delete()
    db_session.query(ReservaSala).delete()
    db_session.query(ProviderSchedule).delete()
    db_session.query(ProviderProfile).delete()
    db_session.query(SessionModel).delete()
    db_session.query(AuditLog).delete()
    db_session.query(User).delete()
    db_session.query(Equipo).delete()
    db_session.query(Sala).delete()
    db_session.commit()