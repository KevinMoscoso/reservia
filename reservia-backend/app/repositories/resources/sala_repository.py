from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.resources.sala import Sala, SalaEstado


def create(db: DBSession, nombre: str, ubicacion: str, capacidad: int) -> Sala:
    sala = Sala(nombre=nombre, ubicacion=ubicacion, capacidad=capacidad)
    db.add(sala)
    db.commit()
    db.refresh(sala)
    return sala


def get_by_id(db: DBSession, id: int) -> Optional[Sala]:
    return db.query(Sala).filter(Sala.id == id).first()


def list_all(db: DBSession) -> list[Sala]:
    return db.query(Sala).all()


def update(db: DBSession, sala: Sala, **campos) -> Sala:
    for key, value in campos.items():
        if value is not None:
            setattr(sala, key, value)
    db.add(sala)
    db.commit()
    db.refresh(sala)
    return sala


def deactivate(db: DBSession, sala: Sala) -> Sala:
    sala.estado = SalaEstado.inactive
    db.add(sala)
    db.commit()
    db.refresh(sala)
    return sala