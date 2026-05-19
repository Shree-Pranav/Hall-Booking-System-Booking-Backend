import uuid


from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from src.data.models.postgres.base import Base




class Booking(Base):


    __tablename__ = "bookings"


    __table_args__ = (
        CheckConstraint(
            "start_datetime < end_datetime",
            name="check_booking_time"
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )


    hall_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("halls.id"),
        nullable=False
    )


    start_datetime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False
    )


    end_datetime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False
    )


    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )


    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
