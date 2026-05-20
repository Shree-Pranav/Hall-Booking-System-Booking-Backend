from __future__ import annotations


from datetime import datetime
from uuid import UUID


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.data.models.postgres.booking import Booking
from src.data.models.postgres.hall import Hall
from src.data.models.postgres.user import User




class BookingRepository:


    def __init__(self, session: AsyncSession):
        self.session = session


    def _build_booking_view_payload(
        self,
        booking: Booking,
        user_name: str,
        hall_name: str,
    ) -> dict:
        return {
            "id": booking.id,
            "user_id": booking.user_id,
            "user_name": user_name,
            "hall_id": booking.hall_id,
            "hall_name": hall_name,
            "start_datetime": booking.start_datetime,
            "end_datetime": booking.end_datetime,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "booking_status": booking.status,
        }


    async def get_hall_by_id(self, hall_id: UUID) -> Hall | None:
        result = await self.session.execute(select(Hall).where(Hall.id == hall_id))
        return result.scalar_one_or_none()


    async def get_hall_by_name(self, hall_name: str) -> Hall | None:
        result = await self.session.execute(select(Hall).where(Hall.name == hall_name))
        return result.scalar_one_or_none()


    async def get_booking_by_id(self, booking_id: UUID) -> Booking | None:
        result = await self.session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()


    async def get_bookings_by_user_id(self, user_id: UUID) -> list[dict]:
        result = await self.session.execute(
            select(
                Booking,
                User.name.label("user_name"),
                Hall.name.label("hall_name"),
            )
            .join(User, User.id == Booking.user_id)
            .join(Hall, Hall.id == Booking.hall_id)
            .where(Booking.user_id == user_id)
            .order_by(Booking.start_datetime.desc())
        )
        rows = result.all()
        return [
            self._build_booking_view_payload(booking, user_name, hall_name)
            for booking, user_name, hall_name in rows
        ]


    async def get_all_bookings(self) -> list[dict]:
        result = await self.session.execute(
            select(
                Booking,
                User.name.label("user_name"),
                Hall.name.label("hall_name"),
            )
            .join(User, User.id == Booking.user_id)
            .join(Hall, Hall.id == Booking.hall_id)
            .order_by(Booking.start_datetime.desc())
        )
        rows = result.all()
        return [
            self._build_booking_view_payload(booking, user_name, hall_name)
            for booking, user_name, hall_name in rows
        ]


    async def cancel_booking(self, booking: Booking) -> None:
        booking.status = "cancelled"
        await self.session.flush()
        await self.session.refresh(booking)


    async def get_overlapping_booking(
        self,
        hall_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> Booking | None:
        query = select(Booking).where(
            Booking.hall_id == hall_id,
            Booking.start_datetime < end_datetime,
            Booking.end_datetime > start_datetime,
        )


        if exclude_booking_id is not None:
            query = query.where(Booking.id != exclude_booking_id)


        result = await self.session.execute(query.order_by(Booking.start_datetime))
        return result.scalar_one_or_none()


    async def create_booking(
        self,
        user_id: UUID,
        hall_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> Booking:
        booking = Booking(
            user_id=user_id,
            hall_id=hall_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status="booked",
        )


        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking


    async def update_booking_timing(
        self,
        booking: Booking,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> Booking:
        booking.start_datetime = start_datetime
        booking.end_datetime = end_datetime


        await self.session.flush()
        await self.session.refresh(booking)
        return booking
