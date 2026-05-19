from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HallCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(..., gt=0)
    floor: int = Field(..., ge=0)


class HallUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    capacity: int | None = Field(None, gt=0)
    floor: int | None = Field(None, ge=0)
    is_active: bool | None = None


class HallOut(BaseModel):
    id: UUID
    name: str
    capacity: int
    floor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HallListOut(BaseModel):
    halls: list[HallOut]
    total: int
