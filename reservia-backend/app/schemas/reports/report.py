from datetime import date

from pydantic import BaseModel


class ResourceOccupancyItem(BaseModel):
    resource_type: str
    resource_id: int
    resource_nombre: str
    reservas_confirmadas: int
    bloques_reservados: int
    bloques_disponibles: int
    porcentaje_ocupacion: float


class OccupancyReportResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    items: list[ResourceOccupancyItem]


class ProviderActivityItem(BaseModel):
    provider_profile_id: int
    provider_full_name: str
    citas_confirmadas: int
    citas_canceladas: int
    total_citas: int


class ProviderActivityReportResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    items: list[ProviderActivityItem]


class SystemActivityReportResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    usuarios_activos: int
    total_reservas_salas: int
    total_reservas_equipos: int
    total_citas: int
    total_general: int
    total_cancelaciones: int
    porcentaje_cancelacion: float