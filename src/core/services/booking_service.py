from __future__ import annotations


from datetime import datetime
from datetime import timezone
from uuid import UUID


from fastapi import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.data.repositories.booking_repository import BookingRepository




class BookingService:


    def __init__(self, session: AsyncSession):
        self.booking_repository = BookingRepository(session)

    def _get_user_id(self, current_user: dict) -> UUID:
        user_id_value = current_user.get("user_id")


        if not user_id_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )


        try:
            return UUID(str(user_id_value))


        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
            )


    async def get_my_bookings(self, current_user: dict):
        # Ensure username is present in JWT, then use token user_id for filtering.
        user_id = self._get_user_id(current_user)


        return await self.booking_repository.get_bookings_by_user_id(user_id)


    async def get_all_bookings(self, current_user: dict):
        return await self.booking_repository.get_all_bookings()


    async def get_bookings_by_user_id(
        self,
        current_user: dict,
        user_id: UUID,
    ):
        return await self.booking_repository.get_bookings_by_user_id(user_id)


    async def cancel_booking(
        self,
        current_user: dict,
        booking_id: UUID,
    ):
        user_id = self._get_user_id(current_user)


        booking = await self.booking_repository.get_booking_by_id(booking_id)


        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )


        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own booking",
            )

        await self.booking_repository.cancel_booking(booking)
        return {"detail": "Booking cancelled successfully"}

    def _validate_time_window(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        if start_datetime >= end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time",
            )


    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value


        return value.astimezone(timezone.utc).replace(tzinfo=None)


    async def _ensure_no_overlap(
        self,
        hall_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_booking_id: UUID | None = None,
    ):
        overlapping_booking = (
            await self.booking_repository.get_overlapping_booking(
                hall_id=hall_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                exclude_booking_id=exclude_booking_id,
            )
        )


        if overlapping_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking time overlaps with an existing booking for this hall",
            )


    async def book_hall(
        self,
        current_user: dict,
        booking_data: dict,
    ):
        user_id = self._get_user_id(current_user)


        hall_name = booking_data["hall_name"]


        start_datetime = self._normalize_datetime(
            booking_data["start_datetime"]
        )


        end_datetime = self._normalize_datetime(
            booking_data["end_datetime"]
        )


        self._validate_time_window(
            start_datetime,
            end_datetime,
        )


        hall = await self.booking_repository.get_hall_by_name(
            hall_name
        )


        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall not found",
            )


        if not hall.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hall is inactive",
            )


        await self._ensure_no_overlap(
            hall.id,
            start_datetime,
            end_datetime,
        )


        try:
            booking = await self.booking_repository.create_booking(
                user_id=user_id,
                hall_id=hall.id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )


            return booking


        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time",
            )


    async def update_booking_timing(
        self,
        current_user: dict,
        booking_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
    ):

        user_id = self._get_user_id(current_user)


        start_datetime = self._normalize_datetime(
            start_datetime
        )


        end_datetime = self._normalize_datetime(
            end_datetime
        )


        self._validate_time_window(
            start_datetime,
            end_datetime,
        )


        booking = await self.booking_repository.get_booking_by_id(
            booking_id
        )


        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )


        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own booking",
            )


        if booking.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancelled booking cannot be updated",
            )


        await self._ensure_no_overlap(
            hall_id=booking.hall_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            exclude_booking_id=booking.id,
        )


        try:
            updated_booking = (
                await self.booking_repository.update_booking_timing(
                    booking=booking,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                )
            )


            return updated_booking


        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time",
            )
        