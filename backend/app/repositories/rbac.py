"""
Nexora Platform — RBAC Repositories
"""

from __future__ import annotations

import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import Role, Permission, UserRole, PermissionGroup, RoleAuditLog
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository handling CRUD and queries for Role records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Role, session=session)

    async def get_by_slug(self, slug: str) -> Role | None:
        """Find role by unique slug."""
        query = select(Role).where(
            Role.slug == slug.lower().strip(),
            Role.is_deleted == False  # noqa: E712
        ).options(selectinload(Role.permissions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_org(self, organization_id: uuid.UUID) -> list[Role]:
        """List active custom tenant roles + system-wide global roles."""
        query = select(Role).where(
            (Role.organization_id == organization_id) | (Role.is_system == True),  # noqa: E712
            Role.is_deleted == False  # noqa: E712
        ).options(selectinload(Role.permissions))
        result = await self.session.execute(query)
        return list(result.scalars().all())


class PermissionRepository(BaseRepository[Permission]):
    """Repository handling CRUD and query actions for Permission nodes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Permission, session=session)

    async def get_by_code(self, permission_code: str) -> Permission | None:
        """Retrieve permission by unique code string (e.g. 'users.create')."""
        query = select(Permission).where(Permission.permission == permission_code.lower().strip())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class UserRoleRepository(BaseRepository[UserRole]):
    """Repository tracking user-to-role mappings scoped by organization."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=UserRole, session=session)

    async def get_user_role(self, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole | None:
        """Resolve specific user-to-role mapping."""
        query = select(UserRole).where(
            UserRole.organization_id == organization_id,
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.status == "active"
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user_org(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> list[UserRole]:
        """List active roles assigned to a user in a target organization."""
        query = select(UserRole).where(
            UserRole.organization_id == organization_id,
            UserRole.user_id == user_id,
            UserRole.status == "active"
        ).options(selectinload(UserRole.role))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_assignment(self, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Delete assignment record."""
        stmt = delete(UserRole).where(
            UserRole.organization_id == organization_id,
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return True


class PermissionGroupRepository(BaseRepository[PermissionGroup]):
    """Repository handling permission grouping models."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=PermissionGroup, session=session)

    async def get_by_name(self, name: str) -> PermissionGroup | None:
        """Find group by name."""
        query = select(PermissionGroup).where(PermissionGroup.name == name.strip())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class RoleAuditLogRepository(BaseRepository[RoleAuditLog]):
    """Repository logging security alterations to roles."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=RoleAuditLog, session=session)
