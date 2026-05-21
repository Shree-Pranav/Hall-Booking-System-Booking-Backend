from datetime import datetime
from datetime import timezone
from uuid import UUID


from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession


from src.data.models.postgres.booking import Booking
from src.data.models.postgres.hall import Hall
from src.data.models.postgres.facility import Facility
from src.data.models.postgres.hall_facility import HallFacility




class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value

        return value.astimezone(timezone.utc).replace(tzinfo=None)


    def _calculate_available_slots(
        self,
        search_start: datetime,
        search_end: datetime,
        bookings: list[Booking],
    ) -> list[dict]:
        """
        Calculate available time slots for a hall based on existing bookings.
        Returns list of dicts with start_time, end_time, and duration_minutes.
        """
        if not bookings:
            # No bookings, entire search window is available
            duration = (search_end - search_start).total_seconds() // 60
            return [
                {
                    "start_time": search_start,
                    "end_time": search_end,
                    "duration_minutes": int(duration),
                }
            ]


        # Sort bookings by start time
        sorted_bookings = sorted(bookings, key=lambda b: b.start_datetime)


        available_slots = []
        current_time = search_start


        for booking in sorted_bookings:
            # Only consider active bookings (not cancelled)
            if booking.status == "cancelled":
                continue


            # If there's a gap before this booking
            if current_time < booking.start_datetime:
                duration = (booking.start_datetime - current_time).total_seconds() // 60
                available_slots.append(
                    {
                        "start_time": current_time,
                        "end_time": booking.start_datetime,
                        "duration_minutes": int(duration),
                    }
                )


            # Move current time past this booking
            if booking.end_datetime > current_time:
                current_time = booking.end_datetime


        # Add remaining slot after last booking
        if current_time < search_end:
            duration = (search_end - current_time).total_seconds() // 60
            available_slots.append(
                {
                    "start_time": current_time,
                    "end_time": search_end,
                    "duration_minutes": int(duration),
                }
            )


        return available_slots


    async def search_halls(
        self,
        search_start: datetime,
        search_end: datetime,
        hall_id: UUID | None = None,
        hall_name: str | None = None,
        facility_id: int | None = None,
        facility_name: str | None = None,
    ) -> list[dict]:
        """
        Search for available halls based on filters.
        Returns halls with their available time slots within the search window.
        """
        search_start = self._normalize_datetime(search_start)
        search_end = self._normalize_datetime(search_end)

        # Build hall query
        hall_query = select(Hall).where(Hall.is_active.is_(True))


        if hall_id:
            hall_query = hall_query.where(Hall.id == hall_id)
        elif hall_name:
            hall_query = hall_query.where(Hall.name == hall_name)


        # If facility filter is provided, join through HallFacility
        if facility_id or facility_name:
            if facility_name:
                hall_query = (
                    hall_query.join(HallFacility, Hall.id == HallFacility.hall_id)
                    .join(Facility, HallFacility.facility_id == Facility.id)
                    .where(
                        Facility.name == facility_name,
                        HallFacility.is_active.is_(True),
                    )
                    .distinct(Hall.id)
                )
            else:  # facility_id
                hall_query = (
                    hall_query.join(HallFacility, Hall.id == HallFacility.hall_id)
                    .where(
                        HallFacility.facility_id == facility_id,
                        HallFacility.is_active.is_(True),
                    )
                    .distinct(Hall.id)
                )


        halls_result = await self.session.execute(hall_query)
        halls = list(halls_result.scalars().all())


        if not halls:
            return []


        results = []


        for hall in halls:
            # Get all bookings for this hall that overlap with search window
            bookings_query = select(Booking).where(
                and_(
                    Booking.hall_id == hall.id,
                    Booking.start_datetime < search_end,
                    Booking.end_datetime > search_start,
                )
            )


            bookings_result = await self.session.execute(bookings_query)
            bookings = list(bookings_result.scalars().all())


            # Calculate available slots
            available_slots = self._calculate_available_slots(
                search_start,
                search_end,
                bookings,
            )


            # Convert to dict format
            slot_dicts = [
                {
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "duration_minutes": slot["duration_minutes"],
                }
                for slot in available_slots
            ]


            results.append(
                {
                    "hall_id": hall.id,
                    "hall_name": hall.name,
                    "capacity": hall.capacity,
                    "floor": hall.floor,
                    "available_slots": slot_dicts,
                }
            )


        return results


