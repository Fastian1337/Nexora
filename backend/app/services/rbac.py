"""
Nexora Platform — Role Based Access Control (RBAC) Service

Orchestrates custom role creation, default seeding, assignments, and Redis-cached
permission checks.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.user import Role, Permission, UserRole, PermissionGroup, RoleAuditLog
from app.models.config import Organization
from app.repositories.rbac import (
    RoleRepository,
    PermissionRepository,
    UserRoleRepository,
    PermissionGroupRepository,
    RoleAuditLogRepository,
)
from app.repositories.organization import OrganizationRepository
from app.config.logging import get_logger

logger = get_logger(__name__)


class RBACService:
    """
    Service layer implementing RBAC lifecycle and cached permission validations.
    """

    def __init__(
        self,
        role_repo: RoleRepository,
        perm_repo: PermissionRepository,
        user_role_repo: UserRoleRepository,
        group_repo: PermissionGroupRepository,
        audit_repo: RoleAuditLogRepository,
        org_repo: OrganizationRepository,
        redis: Redis,
    ) -> None:
        self.role_repo = role_repo
        self.perm_repo = perm_repo
        self.user_role_repo = user_role_repo
        self.group_repo = group_repo
        self.audit_repo = audit_repo
        self.org_repo = org_repo
        self.redis = redis

    def _get_cache_key(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> str:
        return f"user:permissions:{user_id}:{organization_id}"

    async def get_user_permissions(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> list[str]:
        """
        Resolve all active permissions for a target user inside an organization.
        Queries Redis cache first, falling back to database loads.
        """
        cache_key = self._get_cache_key(user_id, organization_id)

        # 1. Try Cache Lookup
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("rbac_cache_lookup_failed", error=str(e))

        # 2. Database Load
        # Retrieve all user role assignments
        assignments = await self.user_role_repo.list_by_user_org(organization_id, user_id)
        
        permissions_set = set()
        for assign in assignments:
            # Load role permissions
            role = await self.role_repo.get_by_id(assign.role_id, organization_id)
            if role and role.status == "active":
                for perm in role.permissions:
                    permissions_set.add(perm.permission)

        permissions_list = list(permissions_set)

        # 3. Write back to Cache
        try:
            await self.redis.setex(cache_key, 3600, json.dumps(permissions_list))
        except Exception as e:
            logger.warning("rbac_cache_write_failed", error=str(e))

        return permissions_list

    async def invalidate_cache(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        """
        Purge the user permissions cache record.
        """
        cache_key = self._get_cache_key(user_id, organization_id)
        try:
            await self.redis.delete(cache_key)
        except Exception as e:
            logger.warning("rbac_cache_invalidation_failed", error=str(e))

    async def has_permission(self, user_id: uuid.UUID, organization_id: uuid.UUID, permission: str) -> bool:
        """
        Security verification check. Returns True if user holds permission.
        Super-user bypass: Organization owner automatically gets all permissions.
        """
        # Resolve organization owner status
        org = await self.org_repo.get_by_id(organization_id, organization_id)
        if org and org.owner_id == user_id:
            return True

        permissions = await self.get_user_permissions(user_id, organization_id)
        return permission in permissions

    async def create_custom_role(
        self,
        name: str,
        slug: str,
        description: str | None,
        organization_id: uuid.UUID,
        creator_id: uuid.UUID,
        permission_ids: list[uuid.UUID] | None = None,
    ) -> Role:
        """
        Register a custom organization-scoped role with mapped permissions.
        """
        # Validate slug uniqueness
        existing = await self.role_repo.get_by_slug(slug)
        if existing:
            raise ConflictException(message="Role slug already exists", error_code="ROLE_SLUG_EXISTS")

        role = Role(
            organization_id=organization_id,
            name=name,
            slug=slug.lower().strip(),
            description=description,
            is_system=False,
            priority=10,
            status="active",
            created_by=creator_id,
            updated_by=creator_id,
        )

        # Load permissions
        if permission_ids:
            for pid in permission_ids:
                perm = await self.perm_repo.get_by_id(pid, organization_id)
                if perm:
                    role.permissions.append(perm)

        created = await self.role_repo.create(role)

        # Log creation audit
        audit = RoleAuditLog(
            organization_id=organization_id,
            user_id=creator_id,
            action="create_role",
            details={"role_id": str(created.id), "name": name, "slug": slug},
        )
        await self.audit_repo.create(audit)

        logger.info("custom_role_created", org_id=str(organization_id), role_id=str(created.id))
        return created

    async def update_custom_role(
        self,
        role_id: uuid.UUID,
        organization_id: uuid.UUID,
        editor_id: uuid.UUID,
        name: str | None = None,
        description: str | None = None,
        permission_ids: list[uuid.UUID] | None = None,
    ) -> Role:
        """
        Modify custom role details and permissions mappings.
        """
        role = await self.role_repo.get_by_id(role_id, organization_id)
        if not role or role.is_system or role.is_deleted:
            raise NotFoundException(message="Custom role not found", error_code="ROLE_NOT_FOUND")

        if name:
            role.name = name
        if description:
            role.description = description
        role.updated_by = editor_id

        if permission_ids is not None:
            role.permissions.clear()
            for pid in permission_ids:
                perm = await self.perm_repo.get_by_id(pid, organization_id)
                if perm:
                    role.permissions.append(perm)

        updated = await self.role_repo.update(role)

        # Invalidate cache for users linked to this role
        query = select(UserRole).where(UserRole.role_id == role_id, UserRole.organization_id == organization_id)
        assignments = (await self.user_role_repo.session.execute(query)).scalars().all()
        for assign in assignments:
            await self.invalidate_cache(assign.user_id, organization_id)

        # Log update audit
        audit = RoleAuditLog(
            organization_id=organization_id,
            user_id=editor_id,
            action="update_role",
            details={"role_id": str(role_id), "name": role.name},
        )
        await self.audit_repo.create(audit)

        logger.info("custom_role_updated", org_id=str(organization_id), role_id=str(role_id))
        return updated

    async def delete_custom_role(self, role_id: uuid.UUID, organization_id: uuid.UUID, editor_id: uuid.UUID) -> None:
        """
        Soft delete custom role. system roles are protected.
        """
        role = await self.role_repo.get_by_id(role_id, organization_id)
        if not role or role.is_system or role.is_deleted:
            raise NotFoundException(message="Custom role not found", error_code="ROLE_NOT_FOUND")

        role.is_deleted = True
        role.deleted_at = datetime.now(timezone.utc)
        await self.role_repo.update(role)

        # Invalidate cache for users linked to this role
        query = select(UserRole).where(UserRole.role_id == role_id, UserRole.organization_id == organization_id)
        assignments = (await self.user_role_repo.session.execute(query)).scalars().all()
        for assign in assignments:
            await self.invalidate_cache(assign.user_id, organization_id)

        # Log delete audit
        audit = RoleAuditLog(
            organization_id=organization_id,
            user_id=editor_id,
            action="delete_role",
            details={"role_id": str(role_id)},
        )
        await self.audit_repo.create(audit)

        logger.info("custom_role_deleted", org_id=str(organization_id), role_id=str(role_id))

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        organization_id: uuid.UUID,
        assigner_id: uuid.UUID,
        expires_at: datetime | None = None,
    ) -> UserRole:
        """
        Assign an active role mapping to a user. Invalidates permission cache.
        """
        role = await self.role_repo.get_by_id(role_id, organization_id)
        if not role or role.is_deleted:
            raise NotFoundException(message="Role not found", error_code="ROLE_NOT_FOUND")

        existing = await self.user_role_repo.get_user_role(organization_id, user_id, role_id)
        if existing:
            return existing

        assignment = UserRole(
            organization_id=organization_id,
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigner_id,
            expires_at=expires_at,
            status="active",
        )

        created = await self.user_role_repo.create(assignment)
        await self.invalidate_cache(user_id, organization_id)

        # Log assignment audit
        audit = RoleAuditLog(
            organization_id=organization_id,
            user_id=assigner_id,
            action="assign_role",
            details={"target_user_id": str(user_id), "role_id": str(role_id)},
        )
        await self.audit_repo.create(audit)

        logger.info("role_assigned", org_id=str(organization_id), user_id=str(user_id), role_id=str(role_id))
        return created

    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID, organization_id: uuid.UUID, remover_id: uuid.UUID) -> None:
        """
        Remove user role assignment mapping.
        """
        await self.user_role_repo.delete_assignment(organization_id, user_id, role_id)
        await self.invalidate_cache(user_id, organization_id)

        # Log removal audit
        audit = RoleAuditLog(
            organization_id=organization_id,
            user_id=remover_id,
            action="remove_role",
            details={"target_user_id": str(user_id), "role_id": str(role_id)},
        )
        await self.audit_repo.create(audit)

        logger.info("role_removed", org_id=str(organization_id), user_id=str(user_id), role_id=str(role_id))

    async def seed_default_roles_and_permissions(self, organization_id: uuid.UUID) -> None:
        """
        Seeds default modular permission nodes, groups, and core system roles
        for a new organization tenant workspace context.
        """
        # 1. Define modular system permissions mapping modules
        permissions_data = [
            ("users", "users.create", "create", "Create organization users", "management"),
            ("users", "users.read", "read", "View organization users list", "management"),
            ("users", "users.update", "update", "Update user profiles", "management"),
            ("users", "users.delete", "delete", "Remove user accounts", "management"),
            
            ("organizations", "organizations.read", "read", "View active organization details", "core"),
            ("organizations", "organizations.update", "update", "Update brand parameters", "core"),
            
            ("knowledge", "knowledge.create", "create", "Upload knowledge files", "agent"),
            ("knowledge", "knowledge.read", "read", "View workspace vectors", "agent"),
            ("knowledge", "knowledge.update", "update", "Edit document categories", "agent"),
            ("knowledge", "knowledge.delete", "delete", "Delete ingested documents", "agent"),
            
            ("chat", "chat.read", "read", "Read chat channels transcripts", "messaging"),
            ("chat", "chat.reply", "reply", "Send chat completions or agent replies", "messaging"),
            ("chat", "chat.delete", "delete", "Remove chat context records", "messaging"),
            
            ("voice", "voice.call", "call", "Initiate voice call campaigns", "telephony"),
            ("voice", "voice.listen", "listen", "Access voice recording streams", "telephony"),
            
            ("marketing", "marketing.generate", "generate", "Generate growth copy content", "campaign"),
            ("marketing", "marketing.publish", "publish", "Auto publish social channels posts", "campaign"),
            ("marketing", "marketing.analytics", "analytics", "Analyze content metrics dashboard", "campaign"),
            
            ("settings", "settings.update", "update", "Modify tenant workspace parameters", "core"),
            ("workflow", "workflow.execute", "execute", "Run custom n8n automations", "core"),
            ("ai", "ai.manage", "manage", "Configure base LLM models settings", "agent"),
            
            ("agent", "agent.manage", "manage", "Create/Delete cognitive worker agents", "agent"),
            ("agent", "agent.train", "train", "Inject prompt instructions to LLM models", "agent"),
            
            ("file", "file.upload", "upload", "Upload branding logo files", "core"),
            ("file", "file.delete", "delete", "Remove media library folders", "core"),
            
            ("notification", "notification.send", "send", "Broadcast notifications broadcasts", "messaging"),
            ("admin", "admin.access", "access", "Access central organizations admin view", "core"),
        ]

        # 2. Seed groups and permission entries
        for mod, perm_code, act, desc, cat in permissions_data:
            # Check or create group
            group = await self.group_repo.get_by_name(mod)
            if not group:
                group = PermissionGroup(name=mod, description=f"Permissions governing the {mod} module")
                group = await self.group_repo.create(group)

            # Check or create permission
            existing_perm = await self.perm_repo.get_by_code(perm_code)
            if not existing_perm:
                perm_obj = Permission(
                    module=mod,
                    permission=perm_code,
                    action=act,
                    description=desc,
                    category=cat,
                    system_permission=True,
                    group_id=group.id,
                )
                await self.perm_repo.create(perm_obj)

        # Resolve all seed permissions
        all_perms_query = select(Permission).where(Permission.system_permission == True)
        all_perms = (await self.perm_repo.session.execute(all_perms_query)).scalars().all()
        perm_map = {p.permission: p for p in all_perms}

        # 3. Setup Default Roles Matrix
        roles_matrix = [
            ("Platform Admin", "platform_admin", "System-wide administration", 90, [
                "users.read", "users.update", "organizations.read", "organizations.update", "admin.access"
            ]),
            ("Organization Owner", "owner", "Full control over organization resources", 100, list(perm_map.keys())),
            ("Organization Admin", "admin", "General administrative functions", 80, [
                k for k in perm_map.keys() if k != "admin.access"
            ]),
            ("Manager", "manager", "Manage agents and campaign publish", 70, [
                "users.read", "knowledge.read", "knowledge.create", "chat.read", "chat.reply",
                "marketing.generate", "marketing.analytics", "settings.update", "file.upload"
            ]),
            ("Receptionist", "receptionist", "Manage chats and appointment schedules", 60, [
                "chat.read", "chat.reply", "knowledge.read", "notification.send"
            ]),
            ("Doctor", "doctor", "View health records and verify visits", 60, [
                "chat.read", "chat.reply", "knowledge.read"
            ]),
            ("Teacher", "teacher", "Monitor school admissions updates", 60, [
                "chat.read", "chat.reply", "knowledge.read"
            ]),
            ("Marketing Manager", "marketing_manager", "Create and analyze campaigns", 60, [
                "marketing.generate", "marketing.publish", "marketing.analytics", "file.upload"
            ]),
            ("Sales Manager", "sales_manager", "Follow-up leads and configure channels", 60, [
                "chat.read", "chat.reply", "voice.call"
            ]),
            ("Employee", "employee", "Standard teammate workspace settings", 30, [
                "chat.read", "chat.reply", "knowledge.read"
            ]),
            ("Viewer", "viewer", "Read-only access across the board", 10, [
                "users.read", "organizations.read", "knowledge.read", "chat.read"
            ]),
        ]

        # Seed Roles & link permissions
        for name, slug, desc, pri, permissions_list in roles_matrix:
            existing_role = await self.role_repo.get_by_slug(slug)
            if not existing_role:
                role_obj = Role(
                    organization_id=organization_id,
                    name=name,
                    slug=slug,
                    description=desc,
                    is_system=True,
                    priority=pri,
                    status="active",
                )
                # Link permission relations
                for p_code in permissions_list:
                    if p_code in perm_map:
                        role_obj.permissions.append(perm_map[p_code])
                
                await self.role_repo.create(role_obj)
            else:
                # Update permissions maps if system roles exist but might be empty
                if not existing_role.permissions:
                    for p_code in permissions_list:
                        if p_code in perm_map:
                            existing_role.permissions.append(perm_map[p_code])
                    await self.role_repo.update(existing_role)
