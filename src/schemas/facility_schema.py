from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic import ConfigDict

class FacilityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FacilitySummary(BaseModel):
    id: UUID
    name: str

