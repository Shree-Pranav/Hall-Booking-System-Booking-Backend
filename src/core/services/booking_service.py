from __future__ import annotations


from datetime import datetime
from datetime import timezone
from uuid import UUID


from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.core.exceptions import (
    BookingConflictException,
    BookingForbiddenException,
    BookingNotFoundException,
    InvalidBookingDataException,
    InvalidTokenException,
)
from src.data.repositories.booking_repository import BookingRepository
from src.observability.logging.logger import instrument_class_methods




@instrument_class_methods
class BookingService:


    def __init__(self, session: AsyncSession):
        self.booking_repository = BookingRepository(session)

    def _get_user_id(self, current_user: dict) -> UUID:
        user_id_value = current_user.get("user_id")


        if not user_id_value:
            raise InvalidTokenException("Invalid token payload")


        try:
            return UUID(str(user_id_value))


        except ValueError:
            raise InvalidTokenException("Invalid user ID format in token")


    async def get_my_bookings(self, current_user: dict):
        # Ensure username is present in JWT, then use token user_id for filtering.
        user_id = self._get_user_id(current_user)


        return await self.booking_repository.get_bookings_by_user_id(
            user_id,
            include_cancelled=False,
        )


    async def get_all_bookings(self, current_user: dict):
        return await self.booking_repository.get_all_bookings()


    async def get_bookings_by_user_id(
        self,
        current_user: dict,
        user_id: UUID,
    ):
        return await self.booking_repository.get_bookings_by_user_id(
            user_id,
            include_cancelled=True,
        )


    async def cancel_booking(
        self,
        current_user: dict,
        booking_id: UUID,
    ):
        user_id = self._get_user_id(current_user)


        booking = await self.booking_repository.get_booking_by_id(booking_id)


        if not booking:
            raise BookingNotFoundException()


        if booking.user_id != user_id:
            raise BookingForbiddenException("You can only cancel your own booking")

        await self.booking_repository.cancel_booking(booking)
        return {"detail": "Booking cancelled successfully"}

    def _validate_time_window(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        if start_datetime >= end_datetime:
            raise InvalidBookingDataException("Start time must be before end time")

        self._validate_half_hour_increment(start_datetime)
        self._validate_half_hour_increment(end_datetime)
        self._validate_not_in_past(start_datetime)


    def _validate_half_hour_increment(self, value: datetime):
        if value.minute not in (0, 30) or value.second != 0 or value.microsecond != 0:
            raise InvalidBookingDataException(
                "Bookings can only start and end on the hour or half hour"
            )


    def _current_utc_naive(self) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)


    def _validate_not_in_past(self, value: datetime):
        if value < self._current_utc_naive():
            raise InvalidBookingDataException("Bookings cannot start in the past")


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
            raise BookingConflictException(
                "Booking time overlaps with an existing booking for this hall"
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
            raise InvalidBookingDataException("Hall not found")


        if not hall.is_active:
            raise InvalidBookingDataException("Hall is inactive")


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
            raise InvalidBookingDataException("Start time must be before end time")


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
            raise BookingNotFoundException()


        if booking.user_id != user_id:
            raise BookingForbiddenException("You can only update your own booking")


        if booking.status == "cancelled":
            raise InvalidBookingDataException("Cancelled booking cannot be updated")


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
            raise InvalidBookingDataException("Start time must be before end time")
        
