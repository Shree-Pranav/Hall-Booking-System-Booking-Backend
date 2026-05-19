from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from src.data.models.postgres.base import Base




class Facility(Base):


    __tablename__ = "facilities"


    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )


    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )


    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
