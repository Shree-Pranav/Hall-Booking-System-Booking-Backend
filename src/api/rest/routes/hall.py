from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import (
    db_session_dependency,
    verify_token,
    verify_admin_role,
    TokenData,
)
from src.core.services.hall_service import HallService
from src.schemas.hall_schema import (
    HallCreate,
    HallFacilityCreate,
    HallFacilityUpdate,
    HallListOut,
    HallOut,
    HallRead,
    HallUpdate,
)


router = APIRouter(prefix="/halls", tags=["halls"])


@router.post("", response_model=HallOut, status_code=status.HTTP_201_CREATED)
async def add_hall(
    hall_in: HallCreate,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> HallOut:
    """Add a new hall (admin only)."""
    service = HallService(db_session)
    return await service.create_hall(hall_in)


@router.post("/add_facility", status_code=status.HTTP_201_CREATED)
async def add_facility_to_hall(
    facility_in: HallFacilityCreate,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> dict[str, str]:
    """Add a facility to a hall (admin only)."""
    service = HallService(db_session)
    return await service.add_facility_to_hall(facility_in)


@router.patch("/facilities", status_code=status.HTTP_200_OK)
async def modify_hall_facility(
    facility_update: HallFacilityUpdate,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> dict[str, str]:
    """Activate or deactivate a hall facility (admin only)."""
    service = HallService(db_session)
    return await service.update_hall_facility(facility_update)


@router.get("/{hall_id}", response_model=HallRead)
async def view_hall(
    hall_id: UUID,
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> HallRead:
    """View a specific hall (users and admins)."""
    service = HallService(db_session)
    return await service.get_hall(hall_id)


@router.get("", response_model=HallListOut)
async def view_halls(
    token_data: Annotated[TokenData, Depends(verify_token)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> HallListOut:
    """View all halls (users and admins)."""
    service = HallService(db_session)
    halls = await service.list_halls()
    return HallListOut(halls=halls, total=len(halls))


@router.patch("/{hall_id}", response_model=HallOut)
async def update_hall(
    hall_id: UUID,
    hall_update: HallUpdate,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> HallOut:
    """Update a hall (admin only)."""
    service = HallService(db_session)
    return await service.update_hall(hall_id, hall_update)


@router.delete("/{hall_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hall(
    hall_id: UUID,
    token_data: Annotated[TokenData, Depends(verify_admin_role)],
    db_session: Annotated[AsyncSession, Depends(db_session_dependency)],
) -> None:
    """Delete a hall (admin only)."""
    service = HallService(db_session)
    await service.delete_hall(hall_id)
