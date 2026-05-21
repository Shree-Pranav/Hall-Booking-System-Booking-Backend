from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.facility import Facility
from src.observability.logging.logger import instrument_class_methods


@instrument_class_methods
class FacilityRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session


    async def create(
        self,
        *,
        name: str,
    ) -> Facility:
        facility = Facility(
            name=name,
        )
        self.db_session.add(facility)
        await self.db_session.flush()
        await self.db_session.refresh(facility)
        return {"id": str(facility.id), "name": facility.name}
    
    async def list_all(self) -> list[Facility]:
        result = await self.db_session.execute(select(Facility).order_by(Facility.created_at.desc()))
        return list(result.scalars().all())
    