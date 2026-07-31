from app.models.resources.sala import Sala, SalaEstado
from app.repositories.resources import sala_repository
from app.repositories.shared import audit_repository
from app.schemas.resources.sala import SalaCreateRequest, SalaUpdateRequest


class SalaNotFoundError(Exception):
    pass


def create_sala(db, data: SalaCreateRequest, actor_user_id: int) -> Sala:
    if data.capacidad <= 0:
        raise ValueError("La capacidad debe ser mayor a 0")

    sala = sala_repository.create(
        db,
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        capacidad=data.capacidad,
    )

    audit_repository.log_action(
        db,
        actor_user_id=actor_user_id,
        action="sala.created",
        entity_type="sala",
        entity_id=sala.id,
        metadata=None,
    )

    return sala


def list_salas(db) -> list[Sala]:
    return sala_repository.list_all(db)


def update_sala(db, sala_id: int, data: SalaUpdateRequest) -> Sala:
    sala = sala_repository.get_by_id(db, sala_id)
    if sala is None:
        raise SalaNotFoundError("sala no encontrada")

    return sala_repository.update(
        db,
        sala,
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        capacidad=data.capacidad,
    )


def deactivate_sala(db, sala_id: int, actor_user_id: int) -> Sala:
    sala = sala_repository.get_by_id(db, sala_id)
    if sala is None:
        raise SalaNotFoundError("sala no encontrada")

    if sala.estado == SalaEstado.inactive:
        return sala

    sala = sala_repository.deactivate(db, sala)

    audit_repository.log_action(
        db,
        actor_user_id=actor_user_id,
        action="sala.deactivated",
        entity_type="sala",
        entity_id=sala.id,
        metadata=None,
    )

    return sala