from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.hall import Hall


class HallRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_id(self, hall_id: UUID) -> Hall | None:
        result = await self.db_session.execute(select(Hall).where(Hall.id == hall_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Hall | None:
        result = await self.db_session.execute(select(Hall).where(Hall.name == name))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Hall]:
        result = await self.db_session.execute(select(Hall).order_by(Hall.created_at.desc()))
        return list(result.scalars().all())

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
        await self.db_session.delete(hall)
        await self.db_session.flush()
