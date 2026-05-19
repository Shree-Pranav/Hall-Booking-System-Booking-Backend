from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)

from src.config.settings import settings


_engine: AsyncEngine | None = None


async def get_or_create_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=10,
            max_overflow=10,
            pool_timeout=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={
                "timeout": 180,
                "command_timeout": 2400,
                "server_settings": {
                    "statement_timeout": "2400000"
                },
            },
        )

    return _engine


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Creates an async session factory."""
    engine = await get_or_create_engine()
    SessionLocal = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    return SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields an async database session."""
    SessionLocal = await get_session_factory()
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise