from __future__ import annotations


from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ResourceNotFoundError
from src.data.models.postgres.favorite import Favorite
from src.data.models.postgres.hall import Hall


class FavoriteRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def list_for_user(self, user_id: UUID) -> list[dict[str, str]]:
        result = await self.db_session.execute(
            select(Hall.id, Hall.name)
            .join(Favorite, Favorite.hall_id == Hall.id)
            .where(
                Favorite.user_id == user_id,
                Hall.is_active.is_(True),
            )
            .order_by(Hall.name)
        )
        return [{"id": str(hall_id), "name": hall_name} for hall_id, hall_name in result.all()]

    async def add(self, user_id: UUID, hall_name: str) -> Favorite:
        hall_result = await self.db_session.execute(
            select(Hall).where(
                Hall.name == hall_name,
                Hall.is_active.is_(True),
            )
        )
        hall = hall_result.scalar_one_or_none()
        if not hall:
            raise ResourceNotFoundError(f"Hall with name {hall_name} not found")

        existing_result = await self.db_session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.hall_id == hall.id,
            )
        )
        favorite = existing_result.scalar_one_or_none()
        if favorite is None:
            favorite = Favorite(user_id=user_id, hall_id=hall.id)
            self.db_session.add(favorite)
            await self.db_session.flush()
            await self.db_session.refresh(favorite)

        return favorite

    async def remove(self, user_id: UUID, hall_name: str) -> None:
        hall_result = await self.db_session.execute(select(Hall).where(Hall.name == hall_name))
        hall = hall_result.scalar_one_or_none()
        if not hall:
            raise ResourceNotFoundError(f"Hall with name {hall_name} not found")

        result = await self.db_session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.hall_id == hall.id,
            )
        )

        favorite = result.scalar_one_or_none()
        if not favorite:
            raise ResourceNotFoundError(f"Favorite hall with name {hall_name} not found for user")

        await self.db_session.delete(favorite)
        await self.db_session.flush()
