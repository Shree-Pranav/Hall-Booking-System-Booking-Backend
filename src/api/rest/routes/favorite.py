from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import TokenData, db_session_dependency, verify_token
from src.core.services.favorite_service import FavoriteService
from src.observability.logging.logger import get_logger, log_function


router = APIRouter(prefix="/favorites", tags=["favorites"])
logger = get_logger(__name__)


@router.post("/add/", status_code=status.HTTP_201_CREATED)
@log_function(logger)
async def add_favorite_hall(
    hall_name: Annotated[str, Query(min_length=1)],
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> dict[str, str]:
    """Add a hall to the authenticated user's favorites."""
    service = FavoriteService(db_session)
    return await service.add_favorite_hall(token_data.user_id, hall_name)


@router.get("/me", status_code=status.HTTP_200_OK)
@log_function(logger)
async def get_my_favorite_halls(
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> list[dict[str, str]]:
    """Return the authenticated user's favorite halls."""
    service = FavoriteService(db_session)
    return await service.list_favorite_halls(token_data.user_id)


@router.delete("/remove/", status_code=status.HTTP_204_NO_CONTENT)
@log_function(logger)
async def remove_favorite_hall(
    hall_name: Annotated[str, Query(min_length=1)],
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> None:
    """Remove a hall from the authenticated user's favorites."""
    service = FavoriteService(db_session)
    await service.remove_favorite_hall(token_data.user_id, hall_name)
