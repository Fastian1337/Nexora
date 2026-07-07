"""
Nexora Platform — Test Configuration

Shared pytest fixtures for unit and integration tests.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings with safe defaults."""
    return Settings(
        app_env="testing",
        app_debug=True,
        app_log_level="DEBUG",
        app_log_format="console",
        database_host="localhost",
        database_port=5432,
        database_name="nexora_test",
        database_user="nexora_user",
        database_password="test_password",
        redis_host="localhost",
        redis_port=6379,
        redis_db=1,
        secret_key="test-secret-key-at-least-32-characters-long",
    )


@pytest.fixture
async def async_client() -> AsyncClient:
    """
    Provide an async HTTP client for integration tests.

    Note: For full integration tests, this should be configured
    with a test database. Will be expanded in the Authentication phase.
    """
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client  # type: ignore[misc]
