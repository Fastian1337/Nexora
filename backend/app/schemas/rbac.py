"""
Nexora Platform — RBAC Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.base import BaseSchema


class PermissionResponse(BaseSchema):
    id: uuid.UUID
    module: str
    permission: str
    action: str
    description: str | None
    category: str
    system_permission: bool


class PermissionGroupResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    permissions: list[PermissionResponse] = []


class RoleCreate(BaseSchema):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9_]+$")
    description: str | None = Field(default=None, max_length=255)
    permission_ids: list[uuid.UUID] | None = Field(default=None)


class RoleUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    permission_ids: list[uuid.UUID] | None = Field(default=None)


class RoleResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID | None
    name: str
    slug: str
    description: str | None
    is_system: bool
    priority: int
    status: str
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime


class RoleAssignRequest(BaseSchema):
    user_id: uuid.UUID
    role_id: uuid.UUID
    expires_at: datetime | None = None


class RoleRemoveRequest(BaseSchema):
    user_id: uuid.UUID
    role_id: uuid.UUID


class RoleAssignmentResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    assigned_by: uuid.UUID | None
    assigned_at: datetime
    expires_at: datetime | None
    status: str
