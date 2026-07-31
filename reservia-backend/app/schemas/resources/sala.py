from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.resources.sala import SalaEstado


class SalaCreateRequest(BaseModel):
    nombre: str = Field(min_length=1)
    ubicacion: str
    capacidad: int

    @field_validator("capacidad")
    @classmethod
    def validate_capacidad(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return value


class SalaUpdateRequest(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1)
    ubicacion: Optional[str] = None
    capacidad: Optional[int] = None

    @field_validator("capacidad")
    @classmethod
    def validate_capacidad(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return value


class SalaResponse(BaseModel):
    id: int
    nombre: str
    ubicacion: str
    capacidad: int
    estado: SalaEstado

    model_config = {"from_attributes": True}