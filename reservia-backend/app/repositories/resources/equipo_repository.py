from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.resources.equipo import Equipo, EquipoEstado


def create(db: DBSession, nombre: str, codigo: str, categoria: str) -> Equipo:
    equipo = Equipo(nombre=nombre, codigo=codigo, categoria=categoria)
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def get_by_id(db: DBSession, id: int) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.id == id).first()


def get_by_codigo(db: DBSession, codigo: str) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.codigo == codigo).first()


def list_all(db: DBSession) -> list[Equipo]:
    return db.query(Equipo).all()


def update(db: DBSession, equipo: Equipo, **campos) -> Equipo:
    for key, value in campos.items():
        if value is not None:
            setattr(equipo, key, value)
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def deactivate(db: DBSession, equipo: Equipo) -> Equipo:
    equipo.estado = EquipoEstado.inactive
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo