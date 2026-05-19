from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.data.repositories.hall_repository import HallRepository
from src.schemas.hall_schema import HallCreate, HallOut, HallUpdate


class HallService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.repository = HallRepository(db_session)
        self.db_session = db_session

    async def create_hall(self, hall_in: HallCreate) -> HallOut:
        """Create a new hall."""
        hall = await self.repository.create(
            name=hall_in.name,
            capacity=hall_in.capacity,
            floor=hall_in.floor,
        )
        await self.db_session.commit()
        return HallOut.model_validate(hall)

    async def get_hall(self, hall_id: UUID) -> HallOut:
        """Get a hall by ID."""
        hall = await self.repository.get_by_id(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")
        return HallOut.model_validate(hall)

    async def list_halls(self) -> list[HallOut]:
        """List all halls."""
        halls = await self.repository.list_all()
        return [HallOut.model_validate(hall) for hall in halls]

    async def update_hall(self, hall_id: UUID, hall_update: HallUpdate) -> HallOut:
        """Update a hall."""
        hall = await self.repository.get_by_id(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")

        updated_hall = await self.repository.update(
            hall,
            name=hall_update.name,
            capacity=hall_update.capacity,
            floor=hall_update.floor,
            is_active=hall_update.is_active,
        )
        await self.db_session.commit()
        return HallOut.model_validate(updated_hall)

    async def delete_hall(self, hall_id: UUID) -> None:
        """Delete a hall."""
        hall = await self.repository.get_by_id(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")

        await self.repository.delete(hall)
        await self.db_session.commit()
