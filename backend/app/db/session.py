"""
Nexora Platform — Database Session Management

Configures the async SQLAlchemy engine and session factory
with connection pooling for PostgreSQL via asyncpg.

Usage:
    from app.db.session import get_db_session

    async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
        result = await db.execute(select(MyModel))
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)

# Module-level references — initialized during app lifespan
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """
    Create and configure the async SQLAlchemy engine.

    Connection pool settings are loaded from application settings.
    This should be called once during application startup.

    Returns:
        AsyncEngine: Configured async database engine.
    """
    global _engine  # noqa: PLW0603

    settings = get_settings()

    _engine = create_async_engine(
        url=settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        pool_pre_ping=True,  # Validate connections before use
    )

    logger.info(
        "database_engine_initialized",
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        pool_size=settings.database_pool_size,
    )

    return _engine


def init_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Create the async session factory.

    Must be called after init_engine().

    Returns:
        async_sessionmaker: Configured session factory.
    """
    global _session_factory  # noqa: PLW0603

    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("database_session_factory_initialized")
    return _session_factory


def get_engine() -> AsyncEngine:
    """
    Get the current database engine.

    Returns:
        AsyncEngine: The active database engine.

    Raises:
        RuntimeError: If the engine has not been initialized.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.

    Yields a session within a transaction scope. The session is
    automatically committed on success or rolled back on error.

    Yields:
        AsyncSession: An async database session.

    Raises:
        RuntimeError: If the session factory has not been initialized.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_session_factory() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_engine() -> None:
    """
    Dispose the database engine and close all connections.

    Should be called during application shutdown.
    """
    global _engine, _session_factory  # noqa: PLW0603

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("database_engine_closed")
