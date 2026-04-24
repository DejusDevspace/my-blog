"""Database engine, async session factory, and base model class."""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

# Naming convention for constraints — ensures Alembic generates deterministic
# migration names and makes it possible to drop constraints by name.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=not settings.is_production,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all ORM models.

    Provides:
    - AsyncAttrs mixin for lazy-loading in async context.
    - Shared metadata with constraint naming conventions.
    - Common `id` primary key column (UUID).
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
