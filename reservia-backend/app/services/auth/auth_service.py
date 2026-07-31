from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from app.core import config
from app.core.security import generate_session_token, hash_password, verify_password
from app.models.auth.user import User, UserRole, UserStatus
from app.repositories.auth import session_repository, user_repository
from app.repositories.shared import audit_repository
from app.schemas.auth.user import (
    CreateProviderRequest,
    LoginRequest,
    RegisterClientRequest,
    SetupAdminRequest,
)


class EmailAlreadyRegisteredError(Exception):
    pass


class SystemAlreadyInitializedError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AccountLockedError(Exception):
    pass


class AccountInactiveError(Exception):
    pass


class NotAuthenticatedError(Exception):
    pass


class SessionExpiredError(Exception):
    pass


def register_client(db: DBSession, data: RegisterClientRequest) -> User:
    if user_repository.get_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError("email ya registrado")

    password_hash = hash_password(data.password)

    try:
        user = user_repository.create_user(
            db,
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            role=UserRole.client,
            status=UserStatus.active,
        )
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyRegisteredError("email ya registrado")

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="user.registered",
        entity_type="user",
        entity_id=user.id,
        metadata=None,
    )

    return user


def bootstrap_admin(db: DBSession, data: SetupAdminRequest) -> User:
    if user_repository.count_by_role(db, UserRole.admin) > 0:
        raise SystemAlreadyInitializedError("sistema ya inicializado")

    password_hash = hash_password(data.password)

    try:
        user = user_repository.create_user(
            db,
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            role=UserRole.admin,
            status=UserStatus.active,
        )
    except IntegrityError:
        db.rollback()
        raise SystemAlreadyInitializedError("sistema ya inicializado")

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="system.bootstrap_completed",
        entity_type="user",
        entity_id=user.id,
        metadata=None,
    )

    return user


def create_provider(db: DBSession, admin_user: User, data: CreateProviderRequest) -> User:
    if user_repository.get_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError("email ya registrado")

    password_hash = hash_password(data.password)

    try:
        user = user_repository.create_user(
            db,
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            role=UserRole.provider,
            status=UserStatus.active,
        )
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyRegisteredError("email ya registrado")

    # Import diferido (dentro de la función, no a nivel de módulo) para
    # mantener auth_service y provider_service desacoplados en tiempo de
    # importación del módulo, según lo indicado por Chat A.
    from app.services.providers.provider_service import ensure_provider_profile

    ensure_provider_profile(db, user_id=user.id)

    audit_repository.log_action(
        db,
        actor_user_id=admin_user.id,
        action="admin.provider_created",
        entity_type="user",
        entity_id=user.id,
        metadata=None,
    )

    return user


def login(db: DBSession, data: LoginRequest) -> tuple[User, str]:
    user = user_repository.get_by_email(db, data.email)

    if user is None:
        audit_repository.log_action(
            db,
            actor_user_id=None,
            action="user.login_failed",
            entity_type="user",
            entity_id=None,
            metadata={"email": data.email, "reason": "not_found"},
        )
        raise InvalidCredentialsError("Credenciales inválidas")

    if user.locked_until is not None and user.locked_until > datetime.utcnow():
        audit_repository.log_action(
            db,
            actor_user_id=user.id,
            action="user.login_blocked",
            entity_type="user",
            entity_id=user.id,
            metadata=None,
        )
        raise AccountLockedError("Cuenta bloqueada temporalmente")

    if user.status == UserStatus.inactive:
        raise AccountInactiveError("Cuenta inactiva")

    if not verify_password(data.password, user.password_hash):
        user = user_repository.increment_failed_attempts(db, user)

        if user.failed_login_attempts >= config.LOGIN_MAX_ATTEMPTS:
            until = datetime.utcnow() + timedelta(minutes=config.LOGIN_LOCKOUT_MINUTES)
            user_repository.set_locked_until(db, user, until)
            user_repository.reset_failed_attempts(db, user)

        audit_repository.log_action(
            db,
            actor_user_id=user.id,
            action="user.login_failed",
            entity_type="user",
            entity_id=user.id,
            metadata=None,
        )
        raise InvalidCredentialsError("Credenciales inválidas")

    user_repository.reset_failed_attempts(db, user)
    token = generate_session_token()
    session_repository.create_session(db, user_id=user.id, token=token)

    audit_repository.log_action(
        db,
        actor_user_id=user.id,
        action="user.login_success",
        entity_type="user",
        entity_id=user.id,
        metadata=None,
    )

    return user, token


def logout(db: DBSession, token: str) -> None:
    session = session_repository.get_by_token(db, token)
    if session is None:
        return

    user_id = session.user_id
    session_repository.delete_session(db, session)

    audit_repository.log_action(
        db,
        actor_user_id=user_id,
        action="user.logout",
        entity_type="user",
        entity_id=user_id,
        metadata=None,
    )


def get_current_user(db: DBSession, token: str | None) -> User:
    if token is None:
        raise NotAuthenticatedError("No autenticado")

    session = session_repository.get_by_token(db, token)
    if session is None:
        raise NotAuthenticatedError("No autenticado")

    inactivity_limit = timedelta(minutes=config.SESSION_INACTIVITY_TIMEOUT_MINUTES)
    if datetime.utcnow() - session.last_seen_at > inactivity_limit:
        session_repository.delete_session(db, session)
        raise SessionExpiredError("Sesión expirada por inactividad")

    session_repository.update_last_seen(db, session)
    return user_repository.get_by_id(db, session.user_id)