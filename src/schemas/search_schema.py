from datetime import datetime
from datetime import timezone
from uuid import UUID


from pydantic import BaseModel, Field, field_serializer


def serialize_utc_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")




class SearchFilters(BaseModel):
    start_datetime: datetime = Field(..., description="Search start datetime")
    end_datetime: datetime = Field(..., description="Search end datetime")
    hall_id: UUID | None = Field(None, description="Optional hall ID filter")
    hall_name: str | None = Field(None, description="Optional hall name filter")
    facility_id: int | None = Field(None, description="Optional facility ID filter")
    facility_name: str | None = Field(None, description="Optional facility name filter")

    @field_serializer("start_datetime", "end_datetime")
    def serialize_datetimes(self, value: datetime) -> str:
        return serialize_utc_datetime(value)


class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int

    @field_serializer("start_time", "end_time")
    def serialize_datetimes(self, value: datetime) -> str:
        return serialize_utc_datetime(value)


class SearchResultHall(BaseModel):
    hall_id: UUID
    hall_name: str
    capacity: int
    floor: int
    available_slots: list[TimeSlot]


class SearchResult(BaseModel):
    search_filters: SearchFilters
    results: list[SearchResultHall]
