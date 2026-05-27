import uuid


from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from src.data.models.postgres.base import Base




class BookingHistory(Base):


    __tablename__ = "booking_history"


    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )


    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )
    
    hall_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("halls.id"),
        nullable=False
    )


    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
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


    logged_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
