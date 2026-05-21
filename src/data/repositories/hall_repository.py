from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.data.models.postgres.hall import Hall
from src.data.models.postgres.hall_facility import HallFacility
from src.data.models.postgres.facility import Facility

class HallRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    def _hall_to_read_dict(self, hall: Hall) -> dict:
        return {
            "id": hall.id,
            "name": hall.name,
            "capacity": hall.capacity,
            "floor": hall.floor,
            "is_active": hall.is_active,
            "created_at": hall.created_at,
            "updated_at": hall.updated_at,
            "facilities": [],
        }

    def _add_facility_row(
        self,
        hall_data: dict,
        hall_facility: HallFacility | None,
        facility: Facility | None,
    ) -> None:
        if not hall_facility or not facility or not hall_facility.is_active:
            return

        hall_data["facilities"].append(
            {
                "facility": {
                    "id": facility.id,
                    "name": facility.name,
                },
                "is_active": hall_facility.is_active,
            }
        )

    async def get_by_id(self, hall_id: UUID) -> Hall | None:
        result = await self.db_session.execute(select(Hall).where(Hall.id == hall_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Hall | None:
        result = await self.db_session.execute(
            select(Hall).where(
                Hall.name == name,
                Hall.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Hall]:
        result = await self.db_session.execute(
            select(Hall)
            .where(Hall.is_active.is_(True))
            .order_by(Hall.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all_with_facilities(self) -> list[dict]:
        result = await self.db_session.execute(
            select(Hall, HallFacility, Facility)
            .outerjoin(HallFacility, Hall.id == HallFacility.hall_id)
            .outerjoin(Facility, Facility.id == HallFacility.facility_id)
            .where(Hall.is_active.is_(True))
            .order_by(Hall.created_at.desc(), Facility.name)
        )

        halls: dict[UUID, dict] = {}
        hall_order: list[UUID] = []

        for hall, hall_facility, facility in result.all():
            hall_data = halls.get(hall.id)
            if hall_data is None:
                hall_data = self._hall_to_read_dict(hall)
                halls[hall.id] = hall_data
                hall_order.append(hall.id)

            self._add_facility_row(hall_data, hall_facility, facility)

        return [halls[hall_id] for hall_id in hall_order]

    async def get_by_id_with_facilities(self, hall_id: UUID) -> dict | None:
        result = await self.db_session.execute(
            select(Hall, HallFacility, Facility)
            .outerjoin(HallFacility, Hall.id == HallFacility.hall_id)
            .outerjoin(Facility, Facility.id == HallFacility.facility_id)
            .where(Hall.id == hall_id)
            .order_by(Facility.name)
        )

        hall_data: dict | None = None
        for hall, hall_facility, facility in result.all():
            if hall_data is None:
                hall_data = self._hall_to_read_dict(hall)

            self._add_facility_row(hall_data, hall_facility, facility)

        return hall_data

    async def create(
        self,
        *,
        name: str,
        capacity: int,
        floor: int,
    ) -> Hall:
        hall = Hall(
            name=name,
            capacity=capacity,
            floor=floor,
            is_active=True,
        )
        self.db_session.add(hall)
        await self.db_session.flush()
        await self.db_session.refresh(hall)
        return hall

    async def update(
        self,
        hall: Hall,
        *,
        name: str | None = None,
        capacity: int | None = None,
        floor: int | None = None,
        is_active: bool | None = None,
    ) -> Hall:
        if name is not None:
            hall.name = name
        if capacity is not None:
            hall.capacity = capacity
        if floor is not None:
            hall.floor = floor
        if is_active is not None:
            hall.is_active = is_active

        await self.db_session.flush()
        await self.db_session.refresh(hall)
        return hall

    async def delete(self, hall: Hall) -> None:
        hall.is_active = False
        await self.db_session.flush()

    async def add_facility_to_hall(self, facility_name: str, hall_name: str) -> dict[str, str]:
        hall = await self.get_by_name(hall_name)
        if not hall:
            raise ResourceNotFoundError(f"Hall with name {hall_name} not found")


        facility = await self.db_session.execute(
            select(Facility).where(Facility.name == facility_name)
        )
        facility = facility.scalar_one_or_none()
        if not facility:
            raise ResourceNotFoundError(f"Facility with name {facility_name} not found")

        existing = await self.db_session.execute(
            select(HallFacility).where(
                HallFacility.hall_id == hall.id,
                HallFacility.facility_id == facility.id,
            )
        )
        hall_facility = existing.scalar_one_or_none()
        if hall_facility:
            hall_facility.is_active = True
        else:
            hall_facility = HallFacility(
                hall_id=hall.id,
                facility_id=facility.id,
                is_active=True,
            )
            self.db_session.add(hall_facility)

        await self.db_session.flush()
        await self.db_session.refresh(hall_facility)
        return {"message": f"Facility '{facility_name}' added to hall '{hall_name}' successfully"}

    async def update_hall_facility(self, hall_name: str, facility_name: str, is_active: bool) -> dict[str, str]:
        hall = await self.get_by_name(hall_name)
        if not hall:
            raise ResourceNotFoundError(f"Hall with name {hall_name} not found")

        facility_result = await self.db_session.execute(
            select(Facility).where(Facility.name == facility_name)
        )
        facility = facility_result.scalar_one_or_none()
        if not facility:
            raise ResourceNotFoundError(f"Facility with name {facility_name} not found")

        hall_facility_result = await self.db_session.execute(
            select(HallFacility).where(
                HallFacility.hall_id == hall.id,
                HallFacility.facility_id == facility.id,
            )
        )
        hall_facility = hall_facility_result.scalar_one_or_none()
        if not hall_facility:
            raise ResourceNotFoundError(
                f"Facility '{facility_name}' is not mapped to hall '{hall_name}'"
            )

        hall_facility.is_active = is_active
        await self.db_session.flush()
        await self.db_session.refresh(hall_facility)
        state = "activated" if is_active else "deactivated"
        return {
            "message": f"Facility '{facility_name}' has been {state} for hall '{hall_name}'"
        }
