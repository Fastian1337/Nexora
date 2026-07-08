"""
Nexora Platform — Role Based Access Control (RBAC) API Router Endpoints

Handles requests querying permissions, managing standard/custom roles, and assigning
roles to tenant teammates.
"""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select

from app.api.deps import get_rbac_service, get_current_user, get_current_organization
from app.api.authorization import RequirePermission, RequireAdmin
from app.models.user import User
from app.models.config import Organization
from app.models.user import Role, Permission
from app.schemas.base import ApiResponse
from app.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionResponse,
    RoleAssignRequest,
    RoleRemoveRequest,
    RoleAssignmentResponse,
)
from app.services.rbac import RBACService

router = APIRouter(prefix="/roles", tags=["Role-Based Access Control"])


@router.get(
    "",
    response_model=ApiResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
    summary="List organization roles",
)
async def list_roles(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Returns custom client roles + standard system-wide roles.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    roles = await rbac_service.role_repo.list_by_org(active_org.id)
    data = [RoleResponse.model_validate(r) for r in roles]
    return {
        "success": True,
        "message": "Roles list retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "",
    response_model=ApiResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireAdmin())],
    summary="Create a custom organization role",
)
async def create_custom_role(
    payload: RoleCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Registers a custom tenant-scoped role with linked permissions. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    role = await rbac_service.create_custom_role(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        organization_id=active_org.id,
        creator_id=current_user.id,
        permission_ids=payload.permission_ids,
    )

    data = RoleResponse.model_validate(role)
    return {
        "success": True,
        "message": "Custom role registered successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.put(
    "/{id}",
    response_model=ApiResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireAdmin())],
    summary="Modify custom role settings",
)
async def update_custom_role(
    id: uuid.UUID,
    payload: RoleUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Updates a custom role's metadata and permission matrix. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    role = await rbac_service.update_custom_role(
        role_id=id,
        organization_id=active_org.id,
        editor_id=current_user.id,
        name=payload.name,
        description=payload.description,
        permission_ids=payload.permission_ids,
    )

    data = RoleResponse.model_validate(role)
    return {
        "success": True,
        "message": "Custom role updated successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.delete(
    "/{id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireAdmin())],
    summary="Remove a custom organization role",
)
async def delete_custom_role(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Performs soft deactivation of a custom organization role. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await rbac_service.delete_custom_role(id, active_org.id, current_user.id)
    return {
        "success": True,
        "message": "Custom role deleted successfully",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/permissions",
    response_model=ApiResponse[list[PermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List granular system permissions",
)
async def list_permissions(
    request: Request,
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Returns lists of all security permission nodes registered in the platform.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    # Query system permissions
    query = select(Permission).order_by(Permission.module, Permission.permission)
    result = await rbac_service.perm_repo.session.execute(query)
    perms = result.scalars().all()

    data = [PermissionResponse.model_validate(p) for p in perms]
    return {
        "success": True,
        "message": "Permissions list retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/assign",
    response_model=ApiResponse[RoleAssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireAdmin())],
    summary="Assign a role to a user",
)
async def assign_role(
    payload: RoleAssignRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Assigns an active role context to a tenant user. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    assignment = await rbac_service.assign_role(
        user_id=payload.user_id,
        role_id=payload.role_id,
        organization_id=active_org.id,
        assigner_id=current_user.id,
        expires_at=payload.expires_at,
    )
    data = RoleAssignmentResponse.model_validate(assignment)
    return {
        "success": True,
        "message": "Role assigned successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/remove",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireAdmin())],
    summary="Remove a role assignment from a user",
)
async def remove_role(
    payload: RoleRemoveRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Revokes role membership allocations for a user. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await rbac_service.remove_role(
        user_id=payload.user_id,
        role_id=payload.role_id,
        organization_id=active_org.id,
        remover_id=current_user.id,
    )
    return {
        "success": True,
        "message": "Role revoked successfully",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/users/{user_id}/permissions",
    response_model=ApiResponse[list[str]],
    status_code=status.HTTP_200_OK,
    summary="Get user permission codes",
)
async def get_user_permissions(
    user_id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Resolves the list of active permission key codes assigned to a user.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    permissions = await rbac_service.get_user_permissions(user_id, active_org.id)
    return {
        "success": True,
        "message": "User permissions resolved successfully",
        "data": permissions,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }
