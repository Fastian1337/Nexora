"""
Nexora Platform — Organization API Router Endpoints

Handles requests managing tenant registrations, config cards, switching workspaces,
adding teammates, and pulling activity audit trails.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select

from app.api.deps import get_organization_service, get_current_user, get_current_organization, get_rbac_service
from app.models.user import User
from app.models.config import Organization, OrganizationSettings, OrganizationInvitation
from app.models.observability import AuditLog
from app.schemas.base import ApiResponse
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationSettingsUpdate,
    OrganizationSettingsResponse,
    OrganizationMemberResponse,
    OrganizationInvitationCreate,
    OrganizationInvitationResponse,
    OrganizationSwitchRequest,
)
from app.services.organization import OrganizationService
from app.services.rbac import RBACService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new organization tenant",
)
async def create_organization(
    payload: OrganizationCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends(get_organization_service),
    rbac_service: RBACService = Depends(get_rbac_service),
) -> dict:
    """
    Registers a new tenant workspace context and links the creator as Owner.
    Sets the active organization context.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    metadata = payload.model_dump(exclude={"name", "slug"})

    org = await org_service.create_organization(
        name=payload.name,
        slug=payload.slug,
        owner_id=current_user.id,
        metadata=metadata,
    )

    # Seed system roles and permissions for this organization
    await rbac_service.seed_default_roles_and_permissions(org.id)

    # Automatically assign "owner" user_role mapping to the creator
    owner_role = await rbac_service.role_repo.get_by_slug("owner")
    if owner_role:
        await rbac_service.assign_role(
            user_id=current_user.id,
            role_id=owner_role.id,
            organization_id=org.id,
            assigner_id=current_user.id,
        )

    data = OrganizationResponse.model_validate(org)
    return {
        "success": True,
        "message": "Organization created successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/me",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve active organization details",
)
async def get_my_organization(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
) -> dict:
    """
    Returns general profile details of the user's currently active workspace context.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    data = OrganizationResponse.model_validate(active_org)
    return {
        "success": True,
        "message": "Organization profile retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.put(
    "",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="Update organization metadata",
)
async def update_organization(
    payload: OrganizationUpdate,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Modifies configuration parameters of the active organization tenant.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    data_dict = payload.model_dump(exclude_unset=True)

    updated = await org_service.update_organization(active_org.id, data_dict)
    data = OrganizationResponse.model_validate(updated)
    return {
        "success": True,
        "message": "Organization updated successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.delete(
    "",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Deactivate organization tenant",
)
async def delete_organization(
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Performs soft deactivation of the active organization. (Owner only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await org_service.delete_organization(active_org.id, current_user.id)
    return {
        "success": True,
        "message": "Organization soft deleted successfully",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/settings",
    response_model=ApiResponse[OrganizationSettingsResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve tenant configurations settings",
)
async def get_settings(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Fetches custom themes, voice language models, logo locations, and active preferences.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    settings = await org_service.get_settings(active_org.id)
    data = OrganizationSettingsResponse.model_validate(settings)
    return {
        "success": True,
        "message": "Organization settings retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.put(
    "/settings",
    response_model=ApiResponse[OrganizationSettingsResponse],
    status_code=status.HTTP_200_OK,
    summary="Update organization config options",
)
async def update_settings(
    payload: OrganizationSettingsUpdate,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Saves updated theme colors, notification setups, custom domains, or voice dialects.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    data_dict = payload.model_dump(exclude_unset=True)

    updated = await org_service.update_settings(active_org.id, data_dict)
    data = OrganizationSettingsResponse.model_validate(updated)
    return {
        "success": True,
        "message": "Organization settings updated successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/members",
    response_model=ApiResponse[list[OrganizationMemberResponse]],
    status_code=status.HTTP_200_OK,
    summary="List organization teammates",
)
async def list_members(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Returns user details of all members linked to the active tenant workspace.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    members = await org_service.get_members_with_details(active_org.id)
    data = [OrganizationMemberResponse.model_validate(m) for m in members]
    return {
        "success": True,
        "message": "Organization members list retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/invite",
    response_model=ApiResponse[OrganizationInvitationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send membership registration invite",
)
async def invite_member(
    payload: OrganizationInvitationCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Creates validation invite token and logs/emails link.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    invite = await org_service.invite_member(
        organization_id=active_org.id,
        email=payload.email,
        role=payload.role,
        inviter_id=current_user.id,
    )
    data = OrganizationInvitationResponse.model_validate(invite)
    return {
        "success": True,
        "message": "Teammate invited successfully. Link active for 7 days.",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/switch",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="Switch active workspace tenant",
)
async def switch_organization(
    payload: OrganizationSwitchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Updates the active organization selection on the user context session.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    org = await org_service.switch_organization(current_user, payload.organization_id)
    data = OrganizationResponse.model_validate(org)
    return {
        "success": True,
        "message": f"Switched active workspace successfully to '{org.name}'",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/activity",
    response_model=ApiResponse[list[dict[str, Any]]],
    status_code=status.HTTP_200_OK,
    summary="Retrieve organization audit activity feed",
)
async def get_activity_feed(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    org_service: OrganizationService = Depends(get_organization_service),
) -> dict:
    """
    Queries active audit trail mutations logged under the organization tenant scope.
    """
    correlation_id = getattr(request.state, "correlation_id", "")

    logs = await org_service.get_activity_logs(active_org.id)

    data = [
        {
            "id": l.id,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
            "user_id": l.user_id,
        }
        for l in logs
    ]

    return {
        "success": True,
        "message": "Organization activity retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }
