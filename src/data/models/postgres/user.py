import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.data.models.postgres.base import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        sa.String(),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        sa.String(20),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        sa.Boolean(),
        server_default=sa.text('true'),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(),
        server_default=sa.text('now()'),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(),
        server_default=sa.text('now()'),
        server_onupdate=sa.text('now()'),
        nullable=False,
    )