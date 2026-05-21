from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.favorite_repository import FavoriteRepository
from src.observability.logging.logger import instrument_class_methods


@instrument_class_methods
class FavoriteService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.repository = FavoriteRepository(db_session)
        self.db_session = db_session

    async def list_favorite_halls(self, user_id: UUID) -> list[dict[str, str]]:
        return await self.repository.list_for_user(user_id)

    async def add_favorite_hall(self, user_id: UUID, hall_name: str) -> dict[str, str]:
        await self.repository.add(user_id, hall_name)
        await self.db_session.commit()
        return {"message": "Hall added to favorites successfully"}

    async def remove_favorite_hall(self, user_id: UUID, hall_name: str) -> dict[str, str]:
        await self.repository.remove(user_id, hall_name)
        await self.db_session.commit()
        return {"message": "Hall removed from favorites successfully"}
