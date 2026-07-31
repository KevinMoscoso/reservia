import datetime

from pydantic import BaseModel, field_validator

from app.models.providers.provider_schedule import DayOfWeek, ScheduleEstado

VALID_DAYS = {day.value for day in DayOfWeek}


class ProviderProfileUpdateRequest(BaseModel):
    slot_duration_minutes: int

    @field_validator("slot_duration_minutes")
    @classmethod
    def validate_slot_duration(cls, value: int) -> int:
        if value < 5 or value > 480:
            raise ValueError("slot_duration_minutes debe estar entre 5 y 480")
        return value


class ProviderProfileResponse(BaseModel):
    id: int
    user_id: int
    slot_duration_minutes: int

    model_config = {"from_attributes": True}


class ScheduleBlockCreateRequest(BaseModel):
    day_of_week: str
    start_time: datetime.time
    end_time: datetime.time

    @field_validator("day_of_week")
    @classmethod
    def validate_day_of_week(cls, value: str) -> str:
        if value not in VALID_DAYS:
            raise ValueError(f"day_of_week debe ser uno de: {sorted(VALID_DAYS)}")
        return value

    @field_validator("end_time")
    @classmethod
    def validate_end_time_after_start(cls, value, info):
        start_time = info.data.get("start_time")
        if start_time is not None and value <= start_time:
            raise ValueError("end_time debe ser mayor a start_time")
        return value


class ScheduleBlockResponse(BaseModel):
    id: int
    provider_profile_id: int
    day_of_week: DayOfWeek
    start_time: datetime.time
    end_time: datetime.time
    estado: ScheduleEstado

    model_config = {"from_attributes": True}


class ProviderPublicResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    slot_duration_minutes: int

    model_config = {"from_attributes": True}