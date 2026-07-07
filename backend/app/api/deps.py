"""
Nexora Platform — Dependency Injection Providers

FastAPI dependencies for injecting shared resources into endpoints.
These providers ensure consistent access to database sessions,
Redis clients, and application settings.

Usage:
    @router.get("/items")
    async def list_items(
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
        settings: Settings = Depends(get_settings_dep),
    ):
        ...
"""

from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import AuthenticationException
from app.db.redis import get_redis_client
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.utils.crypto import decode_jwt_token

reusable_oauth2 = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session.

    Wraps the session module's generator for use as a FastAPI dependency.

    Yields:
        AsyncSession: An async database session with automatic
                      commit/rollback handling.
    """
    async for session in get_db_session():
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Provide an async Redis client.

    Wraps the Redis module's generator for use as a FastAPI dependency.

    Yields:
        Redis: An async Redis client instance.
    """
    async for client in get_redis_client():
        yield client


def get_settings_dep() -> Settings:
    """
    Provide application settings.

    Returns the cached settings singleton for use as a FastAPI dependency.

    Returns:
        Settings: Application settings instance.
    """
    return get_settings()


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """
    Dependency that returns an instantiated UserRepository.
    """
    return UserRepository(session=db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    redis: Redis = Depends(get_redis),
    settings: Settings = Depends(get_settings_dep),
) -> AuthService:
    """
    Dependency that returns an instantiated AuthService.
    """
    return AuthService(user_repository=user_repo, redis_client=redis, settings=settings)


async def get_current_user(
    token_credentials: HTTPAuthorizationCredentials | None = Depends(reusable_oauth2),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Dependency that parses and verifies access tokens, resolving the active User object.
    """
    if not token_credentials:
        raise AuthenticationException(
            message="Not authenticated",
            error_code="NOT_AUTHENTICATED",
        )

    token = token_credentials.credentials
    # Decode access token
    payload = decode_jwt_token(token, expected_type="access")
    user_id = payload.get("sub")
    
    if not user_id:
        raise AuthenticationException(
            message="Invalid token structure",
            error_code="INVALID_TOKEN",
        )

    # Fetch user using a dummy/placeholder organization ID (ignores multi-tenant checks for core authentication)
    # We load user regardless of organization context for auth check
    user = await user_repo.get_by_email(payload.get("email", ""))
    
    if not user:
        raise AuthenticationException(
            message="User associated with token not found",
            error_code="USER_NOT_FOUND",
        )
        
    if not user.is_active:
        raise AuthenticationException(
            message="Account is deactivated",
            error_code="USER_DEACTIVATED",
        )

    return user

