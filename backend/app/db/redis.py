"""
Nexora Platform — Redis Connection Manager

Manages async Redis connections with connection pooling
for caching, sessions, and pub/sub.

Usage:
    from app.db.redis import get_redis_client

    async def my_endpoint(redis: Redis = Depends(get_redis_client)):
        await redis.set("key", "value", ex=300)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)

# Module-level references — initialized during app lifespan
_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None


def init_redis() -> Redis:
    """
    Initialize the async Redis client with connection pooling.

    Should be called once during application startup.

    Returns:
        Redis: Configured async Redis client.
    """
    global _redis_pool, _redis_client  # noqa: PLW0603

    settings = get_settings()

    _redis_pool = ConnectionPool.from_url(
        url=settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
        health_check_interval=30,
    )

    _redis_client = Redis(connection_pool=_redis_pool)

    logger.info(
        "redis_client_initialized",
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        max_connections=settings.redis_max_connections,
    )

    return _redis_client


def get_redis() -> Redis:
    """
    Get the current Redis client instance.

    Returns:
        Redis: The active Redis client.

    Raises:
        RuntimeError: If Redis has not been initialized.
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return _redis_client


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency that provides an async Redis client.

    Yields:
        Redis: An async Redis client.

    Raises:
        RuntimeError: If Redis has not been initialized.
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    yield _redis_client


async def check_redis_health() -> bool:
    """
    Check if Redis is reachable by sending a PING.

    Returns:
        True if Redis responds, False otherwise.
    """
    if _redis_client is None:
        return False
    try:
        return await _redis_client.ping()
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        return False


async def close_redis() -> None:
    """
    Close the Redis connection pool.

    Should be called during application shutdown.
    """
    global _redis_pool, _redis_client  # noqa: PLW0603

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None

    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None

    logger.info("redis_connection_closed")
