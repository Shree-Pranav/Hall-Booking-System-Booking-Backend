from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic import ConfigDict

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

class FacilitySummary(BaseModel):
    id: int
    name: str
model_config = {"from_attributes": True}


class HallListOut(BaseModel):
    halls: list[HallRead]
    total: int


class HallFacilityRead(BaseModel):
    facility: FacilitySummary
    is_active: bool




class HallFacilityCreate(BaseModel):
    facility_name: str
    hall_name: str




class HallFacilityUpdate(BaseModel):
    hall_name: str
    facility_name: str
    is_active: bool



class HallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: UUID
    name: str
    capacity: int
    floor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    facilities: list[HallFacilityRead] = Field(default_factory=list)
