from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.data.repositories.booking_repository import BookingRepository
from src.data.repositories.hall_repository import HallRepository
from src.core.services.notification_service import notification_hub
from src.observability.logging.logger import instrument_class_methods
from src.schemas.hall_schema import (
    HallCreate,
    HallFacilityCreate,
    HallFacilityUpdate,
    HallOut,
    HallRead,
    HallUpdate,
)


@instrument_class_methods
class HallService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.repository = HallRepository(db_session)
        self.booking_repository = BookingRepository(db_session)
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

    async def get_hall(self, hall_id: UUID) -> HallRead:
        """Get a hall by ID."""
        hall = await self.repository.get_by_id_with_facilities(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")
        return HallRead.model_validate(hall)

    async def list_halls(self, include_inactive: bool = False) -> list[HallRead]:
        """List all halls."""
        halls = await self.repository.list_all_with_facilities(
            active_only=not include_inactive,
        )
        return [HallRead.model_validate(hall) for hall in halls]

    async def update_hall(self, hall_id: UUID, hall_update: HallUpdate) -> HallOut:
        """Update a hall."""
        hall = await self.repository.get_by_id(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")

        affected_user_ids: list[UUID] = []
        if hall_update.is_active is False and hall.is_active:
            affected_user_ids = (
                await self.booking_repository.get_active_booking_user_ids_for_hall(
                    hall.id
                )
            )
            await self.booking_repository.cancel_bookings_for_hall(hall.id)

        updated_hall = await self.repository.update(
            hall,
            name=hall_update.name,
            capacity=hall_update.capacity,
            floor=hall_update.floor,
            is_active=hall_update.is_active,
        )
        await self.db_session.commit()
        if affected_user_ids:
            await notification_hub.notify_hall_disabled(
                affected_user_ids,
                hall.id,
                hall.name,
            )
        return HallOut.model_validate(updated_hall)

    async def delete_hall(self, hall_id: UUID) -> None:
        """Deactivate a hall and cancel its active bookings."""
        hall = await self.repository.get_by_id(hall_id)
        if not hall:
            raise ResourceNotFoundError(f"Hall with ID {hall_id} not found")

        affected_user_ids = (
            await self.booking_repository.get_active_booking_user_ids_for_hall(hall.id)
        )
        await self.booking_repository.cancel_bookings_for_hall(hall.id)
        await self.repository.delete(hall)
        await self.db_session.commit()
        if affected_user_ids:
            await notification_hub.notify_hall_disabled(
                affected_user_ids,
                hall.id,
                hall.name,
            )

    async def add_facility_to_hall(self, facility_in: HallFacilityCreate) -> dict[str, str]:
        """Add a facility to a hall."""
        facility = await self.repository.add_facility_to_hall(
            facility_in.facility_name,
            facility_in.hall_name,
        )
        await self.db_session.commit()
        return facility

    async def update_hall_facility(self, facility_update: HallFacilityUpdate) -> dict[str, str]:
        """Update a hall facility's active status."""
        facility = await self.repository.update_hall_facility(
            facility_update.hall_name,
            facility_update.facility_name,
            facility_update.is_active,
        )
        await self.db_session.commit()
        return facility
