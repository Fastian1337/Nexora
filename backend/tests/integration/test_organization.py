"""
Nexora Platform — Organization Service Integration Tests

Validates API routing, payload validation, status codes, and multi-tenant
scoping rules using dependency overrides to mock database state.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import Depends
from httpx import AsyncClient

from app.api.deps import get_organization_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization, OrganizationSettings, OrganizationMember, OrganizationInvitation
from app.main import app


# 1. Setup Mock Models & Services
mock_user_id = uuid.uuid4()
mock_org_id = uuid.uuid4()

mock_user = User(
    id=mock_user_id,
    organization_id=mock_org_id,
    email="test_owner@nexora.ai",
    username="test_owner",
    first_name="Test",
    last_name="Owner",
    is_active=True,
    email_verified=True,
)

mock_organization = Organization(
    id=mock_org_id,
    name="Test Corp",
    slug="test-corp",
    status="active",
    owner_id=mock_user_id,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_settings = OrganizationSettings(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    theme="dark",
    voice_language="en",
    brand_colors={"primary": "#2563EB", "secondary": "#4338CA", "accent": "#06B6D4"},
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)


class MockMemberRepo:
    async def get_member(self, organization_id, user_id):
        return OrganizationMember(
            id=uuid.uuid4(),
            organization_id=organization_id,
            user_id=user_id,
            role="owner",
        )


class MockOrganizationService:
    def __init__(self) -> None:
        self.member_repo = MockMemberRepo()

    async def create_organization(self, name, slug, owner_id, metadata=None) -> Organization:
        return Organization(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            status="active",
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def get_organization(self, organization_id) -> Organization:
        if organization_id == mock_org_id:
            return mock_organization
        return Organization(
            id=organization_id,
            name="Target Corp",
            slug="target-corp",
            status="active",
            owner_id=mock_user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def update_organization(self, organization_id, data) -> Organization:
        return mock_organization

    async def delete_organization(self, organization_id, current_user_id) -> None:
        pass

    async def get_settings(self, organization_id) -> OrganizationSettings:
        return mock_settings

    async def update_settings(self, organization_id, data) -> OrganizationSettings:
        return mock_settings

    async def get_members_with_details(self, organization_id) -> list[dict]:
        return [
            {
                "membership_id": uuid.uuid4(),
                "user_id": mock_user_id,
                "email": "test_owner@nexora.ai",
                "username": "test_owner",
                "first_name": "Test",
                "last_name": "Owner",
                "role": "owner",
                "joined_at": datetime.now(timezone.utc),
            }
        ]

    async def switch_organization(self, user, target_org_id) -> Organization:
        return mock_organization

    async def invite_member(self, organization_id, email, role, inviter_id) -> OrganizationInvitation:
        return OrganizationInvitation(
            id=uuid.uuid4(),
            organization_id=organization_id,
            email=email,
            role=role,
            token="mock_invite_token_123",
            status="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            invited_by=inviter_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


# Setup fixture dependency injection overrides
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_organization_service] = lambda: MockOrganizationService()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_organization_endpoint(async_client: AsyncClient) -> None:
    """Validate registering via POST /api/v1/organizations router."""
    payload = {
        "name": "New Ventures",
        "slug": "new-ventures",
        "business_type": "corporation",
        "industry": "finance",
    }
    response = await async_client.post("/api/v1/organizations", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "New Ventures"
    assert json_data["data"]["slug"] == "new-ventures"


@pytest.mark.asyncio
async def test_get_profile_endpoint(async_client: AsyncClient) -> None:
    """Validate fetching via GET /api/v1/organizations/me router."""
    response = await async_client.get("/api/v1/organizations/me")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Test Corp"


@pytest.mark.asyncio
async def test_update_profile_endpoint(async_client: AsyncClient) -> None:
    """Validate updating via PUT /api/v1/organizations router."""
    payload = {"name": "Updated Corp", "phone": "+923000000000"}
    response = await async_client.put("/api/v1/organizations", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_delete_profile_endpoint(async_client: AsyncClient) -> None:
    """Validate soft deleting via DELETE /api/v1/organizations router."""
    response = await async_client.delete("/api/v1/organizations")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_get_settings_endpoint(async_client: AsyncClient) -> None:
    """Validate settings fetch via GET /api/v1/organizations/settings router."""
    response = await async_client.get("/api/v1/organizations/settings")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["theme"] == "dark"


@pytest.mark.asyncio
async def test_update_settings_endpoint(async_client: AsyncClient) -> None:
    """Validate settings update via PUT /api/v1/organizations/settings router."""
    payload = {"theme": "light", "voice_language": "ur"}
    response = await async_client.put("/api/v1/organizations/settings", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_list_members_endpoint(async_client: AsyncClient) -> None:
    """Validate members list fetch via GET /api/v1/organizations/members router."""
    response = await async_client.get("/api/v1/organizations/members")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["role"] == "owner"


@pytest.mark.asyncio
async def test_invite_member_endpoint(async_client: AsyncClient) -> None:
    """Validate sending invitations via POST /api/v1/organizations/invite router."""
    payload = {"email": "assistant@nexora.ai", "role": "receptionist"}
    response = await async_client.post("/api/v1/organizations/invite", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "assistant@nexora.ai"
    assert json_data["data"]["role"] == "receptionist"


@pytest.mark.asyncio
async def test_switch_workspace_endpoint(async_client: AsyncClient) -> None:
    """Validate switching workspaces via POST /api/v1/organizations/switch router."""
    target_uuid = str(uuid.uuid4())
    payload = {"organization_id": target_uuid}
    response = await async_client.post("/api/v1/organizations/switch", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_activity_endpoint(async_client: AsyncClient) -> None:
    """Validate activity stream fetch via GET /api/v1/organizations/activity router."""
    response = await async_client.get("/api/v1/organizations/activity")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
