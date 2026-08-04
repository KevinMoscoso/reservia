from datetime import date, time

from pydantic import BaseModel, Field, field_validator

from app.models.reservations.reserva_sala import EstadoReserva


class BookingCreateRequest(BaseModel):
    fecha: date
    hora_inicio: time
    num_bloques: int = Field(ge=1, le=20)
    motivo: str = Field(min_length=1)

    @field_validator("fecha")
    @classmethod
    def validate_fecha_not_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("La fecha no puede ser anterior a hoy")
        return value


class ReservaSalaResponse(BaseModel):
    id: int
    sala_id: int
    user_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    motivo: str
    estado: EstadoReserva

    model_config = {"from_attributes": True}


class ReservaEquipoResponse(BaseModel):
    id: int
    equipo_id: int
    user_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    motivo: str
    estado: EstadoReserva

    model_config = {"from_attributes": True}


class CitaResponse(BaseModel):
    id: int
    provider_profile_id: int
    user_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    motivo: str
    estado: EstadoReserva

    model_config = {"from_attributes": True}


class AvailabilityBlockResponse(BaseModel):
    hora_inicio: time
    hora_fin: time
    disponible: bool