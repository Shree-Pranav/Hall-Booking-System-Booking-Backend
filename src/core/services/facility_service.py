from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.facility_repository import FacilityRepository
from src.observability.logging.logger import instrument_class_methods
from src.schemas.facility_schema import FacilityCreate, FacilitySummary


@instrument_class_methods
class FacilityService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.repository = FacilityRepository(db_session)

    async def create_facility(self, facility_in: FacilityCreate) -> dict:
        """Create a new facility."""
        facility = await self.repository.create(
            name=facility_in.name,
        )
        return facility
    
    async def list_facilities(self) -> list[FacilitySummary]:
        """List all facilities."""
        facilities = await self.repository.list_all()
        return [FacilitySummary(id=facility.id, name=facility.name) for facility in facilities]
