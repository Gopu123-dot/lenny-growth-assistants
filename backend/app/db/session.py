"""Database engine and session management with dual storage resilience."""

import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
# Import models so Base.metadata is fully populated
import app.models # noqa: F401


# Global engine and sessionmaker
engine = None
AsyncSessionLocal = None
_active_db_type = "unknown"


async def init_db_engine():
    """Initializes the database engine with fallback capability."""
    global engine, AsyncSessionLocal, _active_db_type

    # Ensure SQLite directory exists if needed
    data_path = Path(settings.DATA_DIR)
    data_path.mkdir(parents=True, exist_ok=True)

    # 1. Attempt primary PostgreSQL connection
    pg_url = settings.DATABASE_URL
    try:
        test_engine = create_async_engine(pg_url, echo=False, pool_pre_ping=True)
        # Attempt a quick ping
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        engine = test_engine
        _active_db_type = "postgresql"
        logger.info("Successfully connected to primary PostgreSQL database", extra={"url": pg_url})
    except Exception as exc:
        logger.warning(
            f"Could not connect to PostgreSQL ({exc}). Checking fallback settings...",
            extra={"error": str(exc)},
        )
        if settings.ENABLE_SQLITE_FALLBACK:
            sqlite_url = settings.SQLITE_DATABASE_URL
            engine = create_async_engine(sqlite_url, echo=False)
            _active_db_type = "sqlite"
            logger.info("Activated SQLite fallback database", extra={"url": sqlite_url})
        else:
            raise exc

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized and verified", extra={"db_type": _active_db_type})


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db_engine()

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_active_db_type() -> str:
    """Returns whether 'postgresql' or 'sqlite' is currently active."""
    return _active_db_type
