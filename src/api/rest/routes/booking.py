from __future__ import annotations


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


from src.api.rest.dependencies import get_current_admin_user
from src.api.rest.dependencies import get_current_user
from src.api.rest.dependencies import get_db_session
from src.observability.logging.logger import get_logger, log_function
from src.core.services.booking_service import BookingService
from src.schemas.booking_schema import BookingCreate
from src.schemas.booking_schema import BookingListRead
from src.schemas.booking_schema import BookingRead
from src.schemas.booking_schema import BookingTimingUpdate


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)
logger = get_logger(__name__)


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
@log_function(logger)

async def book_hall(
    booking_data: BookingCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.book_hall(current_user, booking_data.model_dump())



@router.get(
    "/me",
    response_model=BookingListRead,
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.get_my_bookings(current_user)




@router.get(
    "/all",
    response_model=BookingListRead,
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def get_all_bookings(
    admin_user: dict = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.get_all_bookings(admin_user)




@router.get(
    "/users/{user_id}",
    response_model=BookingListRead,
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def get_bookings_by_user_id(
    user_id: UUID = Path(..., description="User ID"),
    admin_user: dict = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.get_bookings_by_user_id(admin_user, user_id)




@router.patch(
    "/{booking_id}/timing",
    response_model=BookingRead,
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def update_booking_timing(
    booking_data: BookingTimingUpdate,
    booking_id: UUID = Path(..., description="Booking ID"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.update_booking_timing(
        current_user,
        booking_id,
        booking_data.start_datetime,
        booking_data.end_datetime,
    )




@router.patch(
    "/{booking_id}",
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def cancel_booking(
    booking_id: UUID = Path(..., description="Booking ID"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    booking_service = BookingService(session)
    return await booking_service.cancel_booking(current_user, booking_id)
