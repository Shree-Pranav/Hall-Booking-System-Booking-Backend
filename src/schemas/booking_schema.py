from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime


from uuid import UUID


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




BookingListRead = list[BookingViewRead]
