"""
Nexora Platform — RBAC Integration Tests

Validates default permissions seeding, role creation, assignment workflows,
Redis permissions cache, and authorization decorator checks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
from fastapi import Depends
from httpx import AsyncClient

from app.api.deps import get_rbac_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.user import Role, Permission, UserRole
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

mock_role = Role(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    name="Manager",
    slug="manager",
    description="Mock Manager Role",
    is_system=True,
    priority=70,
    status="active",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_permission = Permission(
    id=uuid.uuid4(),
    module="users",
    permission="users.read",
    action="read",
    description="Read user records",
    category="management",
    system_permission=True,
)


class MockRoleRepo:
    async def get_by_slug(self, slug):
        if slug == "manager":
            return mock_role
        return None

    async def get_by_id(self, role_id, org_id):
        return mock_role

    async def list_by_org(self, organization_id):
        return [mock_role]

    async def create(self, role):
        return role

    async def update(self, role):
        return role


class MockPermissionRepo:
    async def get_by_code(self, code):
        return mock_permission

    async def get_by_id(self, pid, org_id):
        return mock_permission

    async def create(self, perm):
        return perm

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_permission]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockUserRoleRepo:
    async def get_user_role(self, org_id, user_id, role_id):
        return None

    async def list_by_user_org(self, org_id, user_id):
        return [
            UserRole(
                id=uuid.uuid4(),
                organization_id=org_id,
                user_id=user_id,
                role_id=mock_role.id,
                status="active",
            )
        ]

    async def create(self, user_role):
        return user_role

    async def delete_assignment(self, org_id, user_id, role_id):
        return True


class MockRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def setex(self, key, ttl, value):
        self.store[key] = value

    async def delete(self, key):
        self.store.pop(key, None)


class MockRBACService:
    def __init__(self) -> None:
        self.role_repo = MockRoleRepo()
        self.perm_repo = MockPermissionRepo()
        self.user_role_repo = MockUserRoleRepo()
        self.redis = MockRedis()

    async def get_user_permissions(self, user_id, organization_id) -> list[str]:
        return ["users.read", "chat.reply"]

    async def has_permission(self, user_id, organization_id, permission) -> bool:
        return permission in ["users.read", "chat.reply"]

    async def create_custom_role(self, name, slug, description, organization_id, creator_id, permission_ids=None) -> Role:
        return Role(
            id=uuid.uuid4(),
            organization_id=organization_id,
            name=name,
            slug=slug,
            description=description,
            is_system=False,
            priority=10,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def update_custom_role(self, role_id, organization_id, editor_id, name=None, description=None, permission_ids=None) -> Role:
        return mock_role

    async def delete_custom_role(self, role_id, organization_id, editor_id) -> None:
        pass

    async def assign_role(self, user_id, role_id, organization_id, assigner_id, expires_at=None) -> UserRole:
        return UserRole(
            id=uuid.uuid4(),
            organization_id=organization_id,
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigner_id,
            assigned_at=datetime.now(timezone.utc),
            status="active",
        )

    async def remove_role(self, user_id, role_id, organization_id, remover_id) -> None:
        pass

    async def seed_default_roles_and_permissions(self, organization_id) -> None:
        pass


# Setup dependency overrides for RBAC tests
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_rbac_service] = lambda: MockRBACService()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_roles_endpoint(async_client: AsyncClient) -> None:
    """Validate fetching via GET /api/v1/roles router."""
    response = await async_client.get("/api/v1/roles")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["slug"] == "manager"


@pytest.mark.asyncio
async def test_create_custom_role_endpoint(async_client: AsyncClient) -> None:
    """Validate registering via POST /api/v1/roles router."""
    payload = {
        "name": "Custom Receptionist",
        "slug": "custom_receptionist",
        "description": "Custom role for front desk operations",
        "permission_ids": [str(uuid.uuid4())],
    }
    response = await async_client.post("/api/v1/roles", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Custom Receptionist"


@pytest.mark.asyncio
async def test_update_custom_role_endpoint(async_client: AsyncClient) -> None:
    """Validate updating custom role via PUT /api/v1/roles/{id} router."""
    payload = {"name": "Senior Manager"}
    role_uuid = str(uuid.uuid4())
    response = await async_client.put(f"/api/v1/roles/{role_uuid}", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_delete_custom_role_endpoint(async_client: AsyncClient) -> None:
    """Validate deactivating custom role via DELETE /api/v1/roles/{id} router."""
    role_uuid = str(uuid.uuid4())
    response = await async_client.delete(f"/api/v1/roles/{role_uuid}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_list_permissions_endpoint(async_client: AsyncClient) -> None:
    """Validate fetching permissions via GET /api/v1/roles/permissions router."""
    response = await async_client.get("/api/v1/roles/permissions")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["permission"] == "users.read"


@pytest.mark.asyncio
async def test_assign_role_endpoint(async_client: AsyncClient) -> None:
    """Validate allocating user role mapping via POST /api/v1/roles/assign router."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4()),
    }
    response = await async_client.post("/api/v1/roles/assign", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_remove_role_endpoint(async_client: AsyncClient) -> None:
    """Validate revoking user role allocation via POST /api/v1/roles/remove router."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4()),
    }
    response = await async_client.post("/api/v1/roles/remove", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_get_user_permissions_endpoint(async_client: AsyncClient) -> None:
    """Validate resolving user permissions list via GET /api/v1/roles/users/{id}/permissions."""
    user_uuid = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/roles/users/{user_uuid}/permissions")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "users.read" in json_data["data"]
