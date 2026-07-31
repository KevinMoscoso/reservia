from sqlalchemy.exc import IntegrityError

from app.models.resources.equipo import Equipo, EquipoEstado
from app.repositories.resources import equipo_repository
from app.repositories.shared import audit_repository
from app.schemas.resources.equipo import EquipoCreateRequest, EquipoUpdateRequest


class EquipoNotFoundError(Exception):
    pass


class CodigoAlreadyExistsError(Exception):
    pass


def create_equipo(db, data: EquipoCreateRequest, actor_user_id: int) -> Equipo:
    if equipo_repository.get_by_codigo(db, data.codigo) is not None:
        raise CodigoAlreadyExistsError("codigo ya registrado")

    try:
        equipo = equipo_repository.create(
            db,
            nombre=data.nombre,
            codigo=data.codigo,
            categoria=data.categoria,
        )
    except IntegrityError:
        db.rollback()
        raise CodigoAlreadyExistsError("codigo ya registrado")

    audit_repository.log_action(
        db,
        actor_user_id=actor_user_id,
        action="equipo.created",
        entity_type="equipo",
        entity_id=equipo.id,
        metadata=None,
    )

    return equipo


def list_equipos(db) -> list[Equipo]:
    return equipo_repository.list_all(db)


def update_equipo(db, equipo_id: int, data: EquipoUpdateRequest) -> Equipo:
    equipo = equipo_repository.get_by_id(db, equipo_id)
    if equipo is None:
        raise EquipoNotFoundError("equipo no encontrado")

    return equipo_repository.update(
        db,
        equipo,
        nombre=data.nombre,
        codigo=data.codigo,
        categoria=data.categoria,
    )


def deactivate_equipo(db, equipo_id: int, actor_user_id: int) -> Equipo:
    equipo = equipo_repository.get_by_id(db, equipo_id)
    if equipo is None:
        raise EquipoNotFoundError("equipo no encontrado")

    if equipo.estado == EquipoEstado.inactive:
        return equipo

    equipo = equipo_repository.deactivate(db, equipo)

    audit_repository.log_action(
        db,
        actor_user_id=actor_user_id,
        action="equipo.deactivated",
        entity_type="equipo",
        entity_id=equipo.id,
        metadata=None,
    )

    return equipo