"""
Nexora Platform — Organization Service

Implements workspace lifecycle, multi-tenant switching actions, configuration
card updates, and team invitation pipelines.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy import select

from app.core.exceptions import AuthenticationException, ConflictException, NotFoundException, ValidationException
from app.models.config import Organization, OrganizationSettings, OrganizationMember, OrganizationInvitation
from app.models.user import User
from app.models.observability import AuditLog
from app.repositories.organization import (
    OrganizationRepository,
    OrganizationSettingsRepository,
    OrganizationMemberRepository,
    OrganizationInvitationRepository,
)
from app.repositories.user import UserRepository
from app.config.logging import get_logger

logger = get_logger(__name__)


class OrganizationService:
    """
    Orchestrates business logic for organization units, settings, and invites.
    """

    def __init__(
        self,
        org_repo: OrganizationRepository,
        settings_repo: OrganizationSettingsRepository,
        member_repo: OrganizationMemberRepository,
        invite_repo: OrganizationInvitationRepository,
        user_repo: UserRepository,
    ) -> None:
        self.org_repo = org_repo
        self.settings_repo = settings_repo
        self.member_repo = member_repo
        self.invite_repo = invite_repo
        self.user_repo = user_repo

    async def create_organization(self, name: str, slug: str, owner_id: uuid.UUID, metadata: dict[str, Any] | None = None) -> Organization:
        """
        Create a new tenant organization.
        Generates corresponding settings record and lists creator as Owner.
        """
        # Validate slug uniqueness
        existing_slug = await self.org_repo.get_by_slug(slug)
        if existing_slug:
            raise ConflictException(
                message="Organization slug already exists",
                error_code="SLUG_EXISTS",
            )

        # Build organization record
        org = Organization(
            name=name,
            slug=slug.lower().strip(),
            owner_id=owner_id,
            status="active",
            business_type=metadata.get("business_type") if metadata else None,
            industry=metadata.get("industry") if metadata else None,
            company_size=metadata.get("company_size") if metadata else None,
            email=metadata.get("email") if metadata else None,
            phone=metadata.get("phone") if metadata else None,
            website=metadata.get("website") if metadata else None,
            country=metadata.get("country") if metadata else None,
            state=metadata.get("state") if metadata else None,
            city=metadata.get("city") if metadata else None,
            timezone=metadata.get("timezone", "UTC") if metadata else "UTC",
            language=metadata.get("language", "en") if metadata else "en",
            currency=metadata.get("currency", "USD") if metadata else "USD",
        )

        created_org = await self.org_repo.create(org)

        # Create settings record
        settings = OrganizationSettings(
            organization_id=created_org.id,
            theme="dark",
            voice_language="en",
            brand_colors={"primary": "#2563EB", "secondary": "#4338CA", "accent": "#06B6D4"},
        )
        await self.settings_repo.create(settings)

        # Link Owner member record
        member = OrganizationMember(
            organization_id=created_org.id,
            user_id=owner_id,
            role="owner",
        )
        await self.member_repo.create(member)

        # Automatically update the user's currently active workspace session
        user = await self.user_repo.get_by_id(owner_id, created_org.id)
        if user:
            user.organization_id = created_org.id
            await self.user_repo.update(user)

        logger.info("organization_created", org_id=str(created_org.id), owner_id=str(owner_id))
        return created_org

    async def get_organization(self, organization_id: uuid.UUID) -> Organization:
        """
        Retrieve active organization details.
        """
        org = await self.org_repo.get_by_id(organization_id, organization_id)
        if not org or org.is_deleted:
            raise NotFoundException(message="Organization not found", error_code="ORGANIZATION_NOT_FOUND")
        return org

    async def update_organization(self, organization_id: uuid.UUID, data: dict[str, Any]) -> Organization:
        """
        Update general organization metadata.
        """
        org = await self.get_organization(organization_id)
        
        for field, val in data.items():
            if hasattr(org, field) and val is not None:
                setattr(org, field, val)

        updated_org = await self.org_repo.update(org)
        logger.info("organization_updated", org_id=str(organization_id))
        return updated_org

    async def delete_organization(self, organization_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        """
        Soft delete organization. Enforces owner constraint check.
        """
        org = await self.get_organization(organization_id)
        if org.owner_id != current_user_id:
            raise AuthenticationException(
                message="Only organization owner can delete organization",
                error_code="OWNER_ONLY_ACTION",
            )

        org.is_deleted = True
        org.deleted_at = datetime.now(timezone.utc)
        await self.org_repo.update(org)
        logger.info("organization_deleted", org_id=str(organization_id))

    async def get_settings(self, organization_id: uuid.UUID) -> OrganizationSettings:
        """
        Retrieve tenant setting cards. Creates default card if not found.
        """
        settings = await self.settings_repo.get_by_org_id(organization_id)
        if not settings:
            # Fallback creation
            settings = OrganizationSettings(
                organization_id=organization_id,
                theme="dark",
                voice_language="en",
                brand_colors={"primary": "#2563EB", "secondary": "#4338CA", "accent": "#06B6D4"},
            )
            settings = await self.settings_repo.create(settings)
        return settings

    async def update_settings(self, organization_id: uuid.UUID, data: dict[str, Any]) -> OrganizationSettings:
        """
        Modify settings parameters.
        """
        settings = await self.get_settings(organization_id)

        for field, val in data.items():
            if hasattr(settings, field) and val is not None:
                setattr(settings, field, val)

        updated = await self.settings_repo.update(settings)
        logger.info("organization_settings_updated", org_id=str(organization_id))
        return updated

    async def get_members_with_details(self, organization_id: uuid.UUID) -> list[dict[str, Any]]:
        """
        Retrieve list of users belonging to the active organization.
        """
        # Resolve members using query join
        query = select(OrganizationMember, User).join(User, OrganizationMember.user_id == User.id).where(
            OrganizationMember.organization_id == organization_id
        )
        result = await self.org_repo.session.execute(query)
        members_list = []
        for member, user in result.all():
            members_list.append({
                "membership_id": member.id,
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": member.role,
                "joined_at": member.created_at,
            })
        return members_list

    async def switch_organization(self, user: User, target_org_id: uuid.UUID) -> Organization:
        """
        Switch user active session to target organization workspace.
        Enforces membership mapping checks.
        """
        # Verify user has valid membership inside target org
        membership = await self.member_repo.get_member(target_org_id, user.id)
        if not membership:
            raise AuthenticationException(
                message="User is not a member of target organization",
                error_code="NOT_MEMBER_OF_ORGANIZATION",
            )

        org = await self.get_organization(target_org_id)

        # Update user active organization link
        user.organization_id = target_org_id
        await self.user_repo.update(user)
        logger.info("user_switched_workspace", user_id=str(user.id), target_org_id=str(target_org_id))
        return org

    async def invite_member(self, organization_id: uuid.UUID, email: str, role: str, inviter_id: uuid.UUID) -> OrganizationInvitation:
        """
        Generate invitation record containing a secure validation token.
        """
        # Verify email is not already a member
        # Resolving if user exists
        user = await self.user_repo.get_by_email(email)
        if user:
            existing_member = await self.member_repo.get_member(organization_id, user.id)
            if existing_member:
                raise ConflictException(
                    message="User with this email is already a member",
                    error_code="ALREADY_MEMBER",
                )

        token = uuid.uuid4().hex
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        invite = OrganizationInvitation(
            organization_id=organization_id,
            email=email.lower().strip(),
            role=role.lower().strip(),
            token=token,
            status="pending",
            expires_at=expires_at,
            invited_by=inviter_id,
        )

        created_invite = await self.invite_repo.create(invite)
        logger.info("member_invited", org_id=str(organization_id), email=email, token=token)
        return created_invite

    async def accept_invitation(self, token: str, user: User) -> OrganizationMember:
        """
        Validate invitation token, register user as team member, and switch active workspace.
        """
        invite = await self.invite_repo.get_by_token(token)
        if not invite or invite.status != "pending":
            raise ValidationException(
                message="Invitation token is invalid or already processed",
                error_code="INVALID_INVITATION",
            )

        # Check expiration
        if invite.expires_at < datetime.now(timezone.utc):
            invite.status = "expired"
            await self.invite_repo.update(invite)
            raise ValidationException(
                message="Invitation has expired",
                error_code="INVITATION_EXPIRED",
            )

        # Confirm recipient email matches active user email
        if invite.email != user.email:
            raise AuthenticationException(
                message="Invitation email does not match authenticated user email",
                error_code="EMAIL_MISMATCH",
            )

        # Create member record
        member = OrganizationMember(
            organization_id=invite.organization_id,
            user_id=user.id,
            role=invite.role,
        )
        created_member = await self.member_repo.create(member)

        # Update invite status
        invite.status = "accepted"
        await self.invite_repo.update(invite)

        # Automatically switch user's active workspace session
        user.organization_id = invite.organization_id
        await self.user_repo.update(user)

        logger.info("invitation_accepted", invite_id=str(invite.id), user_id=str(user.id))
        return created_member

    async def reject_invitation(self, token: str, user: User) -> None:
        """
        Reject invitation.
        """
        invite = await self.invite_repo.get_by_token(token)
        if not invite or invite.status != "pending":
            raise ValidationException(
                message="Invitation is invalid or already processed",
                error_code="INVALID_INVITATION",
            )

        if invite.email != user.email:
            raise AuthenticationException(
                message="Invitation email does not match authenticated user email",
                error_code="EMAIL_MISMATCH",
            )

        invite.status = "rejected"
        await self.invite_repo.update(invite)
        logger.info("invitation_rejected", invite_id=str(invite.id), user_id=str(user.id))

    async def get_activity_logs(self, organization_id: uuid.UUID) -> list[AuditLog]:
        """
        Query audit logs belonging to active organization context.
        """
        query = (
            select(AuditLog)
            .where(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.desc())
            .limit(20)
        )
        result = await self.org_repo.session.execute(query)
        return list(result.scalars().all())
