"""
Nexora Platform — Authorization Dependencies & Decorators

Reusable FastAPI dependencies checking tenant permissions, roles mappings,
and owner bounds.
"""

from __future__ import annotations

from fastapi import Depends

from app.api.deps import get_current_user, get_current_organization, get_organization_service, get_organization_member_repository
from app.api.deps import get_organization_repository # Fallback repositories helper if needed
from app.core.exceptions import AuthenticationException
from app.models.user import User
from app.models.config import Organization
from app.services.organization import OrganizationService
from app.repositories.rbac import UserRoleRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from sqlalchemy import select
from app.models.user import UserRole, Role


class RequirePermission:
    """
    Asserts the authenticated user holds a specific permission code in the active tenant workspace.
    """

    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        active_org: Organization = Depends(get_current_organization),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        # Import dynamically to avoid circular dependencies
        from app.db.redis import get_redis_client
        from app.repositories.rbac import RoleRepository, PermissionRepository, UserRoleRepository, PermissionGroupRepository, RoleAuditLogRepository
        from app.repositories.organization import OrganizationRepository
        from app.services.rbac import RBACService

        redis_client = get_redis_client()
        role_repo = RoleRepository(session=db)
        perm_repo = PermissionRepository(session=db)
        user_role_repo = UserRoleRepository(session=db)
        group_repo = PermissionGroupRepository(session=db)
        audit_repo = RoleAuditLogRepository(session=db)
        org_repo = OrganizationRepository(session=db)

        rbac_service = RBACService(
            role_repo=role_repo,
            perm_repo=perm_repo,
            user_role_repo=user_role_repo,
            group_repo=group_repo,
            audit_repo=audit_repo,
            org_repo=org_repo,
            redis=redis_client,
        )

        has_access = await rbac_service.has_permission(current_user.id, active_org.id, self.permission)
        if not has_access:
            raise AuthenticationException(
                message="You do not have the required permissions to perform this action.",
                error_code="INSUFFICIENT_PERMISSIONS",
            )


class RequireRole:
    """
    Asserts the user is assigned a specific role (by slug) in the active organization context.
    """

    def __init__(self, role_slug: str) -> None:
        self.role_slug = role_slug

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        active_org: Organization = Depends(get_current_organization),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        # Check active organization owner bypass
        if active_org.owner_id == current_user.id:
            return

        # Query user roles mappings
        query = (
            select(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                UserRole.organization_id == active_org.id,
                UserRole.status == "active",
                Role.slug == self.role_slug.lower().strip()
            )
        )
        result = await db.execute(query)
        role_mapping = result.scalar_one_or_none()

        if not role_mapping:
            raise AuthenticationException(
                message=f"Access Denied: Required role '{self.role_slug}' is missing.",
                error_code="ROLE_ACCESS_DENIED",
            )


class RequireOwner:
    """
    Asserts the authenticated user is the registered Owner of the active organization context.
    """

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        active_org: Organization = Depends(get_current_organization),
    ) -> None:
        if active_org.owner_id != current_user.id:
            raise AuthenticationException(
                message="Access Denied: Only the Organization Owner can perform this action.",
                error_code="OWNER_ACCESS_DENIED",
            )


class RequireAdmin:
    """
    Asserts the user holds an Admin or Owner privilege level in the active organization context.
    """

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        active_org: Organization = Depends(get_current_organization),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        if active_org.owner_id == current_user.id:
            return

        # Query user roles for Owner or Admin
        query = (
            select(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                UserRole.organization_id == active_org.id,
                UserRole.status == "active",
                Role.slug.in_(["owner", "admin"])
            )
        )
        result = await db.execute(query)
        role_mapping = result.scalar_one_or_none()

        if not role_mapping:
            raise AuthenticationException(
                message="Access Denied: Admin or Owner privilege level required.",
                error_code="ADMIN_ACCESS_DENIED",
            )
