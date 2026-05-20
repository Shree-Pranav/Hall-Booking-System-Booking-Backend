from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.facility_schema import FacilityCreate, FacilitySummary
from src.core.services.facility_service import FacilityService


from src.api.rest.dependencies import (
    db_session_dependency,
    verify_token,
    verify_admin_role,
    TokenData,
)

router = APIRouter(prefix="/facilities", tags=["facilities"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_facility(
    facility_in: FacilityCreate,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> dict:
    """Add a new facility (admin only)."""
    service = FacilityService(db_session)
    return await service.create_facility(facility_in)   

@router.get("", status_code=status.HTTP_200_OK)
async def view_facilities(
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> list[FacilitySummary]:
    """View all facilities (users and admins)."""
    service = FacilityService(db_session)
    return await service.list_facilities()
