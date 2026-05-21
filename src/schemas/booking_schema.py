from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_serializer
from datetime import datetime
from datetime import timezone


from uuid import UUID


def serialize_utc_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


class BookingCreate(BaseModel):
    hall_name: str
    start_datetime: datetime
    end_datetime: datetime


class BookingTimingUpdate(BaseModel):
    start_datetime: datetime
    end_datetime: datetime


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    hall_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    @field_serializer(
        "start_datetime",
        "end_datetime",
        "created_at",
        "updated_at",
    )
    def serialize_datetimes(self, value: datetime) -> str:
        return serialize_utc_datetime(value)




class BookingViewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: UUID
    user_id: UUID
    user_name: str
    hall_id: UUID
    hall_name: str
    start_datetime: datetime
    end_datetime: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    @field_serializer(
        "start_datetime",
        "end_datetime",
        "created_at",
        "updated_at",
    )
    def serialize_datetimes(self, value: datetime) -> str:
        return serialize_utc_datetime(value)




BookingListRead = list[BookingViewRead]
