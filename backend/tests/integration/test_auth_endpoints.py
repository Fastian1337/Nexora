"""
Nexora Platform — Authentication Integration Tests

Simulates API client requests mapping to the 10 authentication routes.
Uses unittest.mock to mock database and Redis calls so tests run fast and
isolate presentation/routing layer behavior.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

from app.api.deps import get_auth_service
from app.core.exceptions import AuthenticationException
from app.models.user import User
from app.schemas.auth import TokenResponse


# Mock representation of Auth service
class MockAuthService:
    async def register(self, payload):
        mock_user = User(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            email=payload.email,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            status="active",
            email_verified=False,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        return mock_user

    async def login(self, payload, ip, agent):
        if payload.password == "IncorrectPass!":
            raise AuthenticationException("Invalid password", "INVALID_CREDENTIALS")
        return TokenResponse(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_in=900,
        )

    async def logout(self, refresh_token):
        pass

    async def rotate_tokens(self, refresh_token):
        return TokenResponse(
            access_token="mock_new_access_token",
            refresh_token="mock_new_refresh_token",
            expires_in=900,
        )


@pytest.fixture
def override_auth_service():
    return MockAuthService()


@pytest.mark.asyncio
async def test_register_endpoint(async_client: AsyncClient, override_auth_service) -> None:
    """Validate registering via POST /api/v1/auth/register router."""
    from app.main import app

    # Override service injection
    app.dependency_overrides[get_auth_service] = lambda: override_auth_service

    payload = {
        "email": "integration@nexora.tech",
        "username": "tester",
        "password": "SecurePassword123!",
        "first_name": "Integration",
        "last_name": "Tester",
    }
    
    response = await async_client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == payload["email"]
    assert json_data["data"]["username"] == payload["username"]


@pytest.mark.asyncio
async def test_login_endpoint(async_client: AsyncClient, override_auth_service) -> None:
    """Validate sign-in authentication routing and cookie output."""
    from app.main import app
    app.dependency_overrides[get_auth_service] = lambda: override_auth_service

    payload = {
        "email": "tester",
        "password": "SecurePassword123!",
        "remember_me": True,
    }

    response = await async_client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["access_token"] == "mock_access_token"
    # Ensure refresh cookie is correctly mapped to browser response header
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == "mock_refresh_token"


@pytest.mark.asyncio
async def test_login_endpoint_failure(async_client: AsyncClient, override_auth_service) -> None:
    """Verify routing response on credential verification failures."""
    from app.main import app
    app.dependency_overrides[get_auth_service] = lambda: override_auth_service

    payload = {
        "email": "tester",
        "password": "IncorrectPass!",
        "remember_me": False,
    }

    response = await async_client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["errors"][0]["error_code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_logout_endpoint(async_client: AsyncClient, override_auth_service) -> None:
    """Verify endpoint successfully deletes active browser authentication cookies."""
    from app.main import app
    app.dependency_overrides[get_auth_service] = lambda: override_auth_service

    # Setup pre-existing login cookies
    async_client.cookies.set("refresh_token", "mock_refresh_token")
    
    response = await async_client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    # Verify cookie deletion
    assert "refresh_token" not in response.cookies or response.cookies["refresh_token"] == ""
