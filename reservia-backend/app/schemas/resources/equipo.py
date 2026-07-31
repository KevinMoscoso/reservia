from typing import Optional

from pydantic import BaseModel

from app.models.resources.equipo import EquipoEstado


class EquipoCreateRequest(BaseModel):
    nombre: str
    codigo: str
    categoria: str


class EquipoUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    categoria: Optional[str] = None


class EquipoResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    categoria: str
    estado: EquipoEstado

    model_config = {"from_attributes": True}