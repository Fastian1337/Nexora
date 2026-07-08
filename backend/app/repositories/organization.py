"""
Nexora Platform — Organization Data Access Repositories

Provides specialized data queries for Organizations, settings, memberships,
and email invitation workflows.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import Organization, OrganizationSettings, OrganizationMember, OrganizationInvitation
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """
    Concrete repository for the Organization tenant model.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Organization, session=session)

    async def get_by_slug(self, slug: str) -> Organization | None:
        """
        Lookup organization by slug.
        """
        query = select(Organization).where(
            Organization.slug == slug.lower(),
            Organization.is_deleted == False  # noqa: E712
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class OrganizationSettingsRepository(BaseRepository[OrganizationSettings]):
    """
    Data queries for tenant-specific configuration settings.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OrganizationSettings, session=session)

    async def get_by_org_id(self, organization_id: uuid.UUID) -> OrganizationSettings | None:
        """
        Resolve configurations mapped to a specific organization.
        """
        query = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == organization_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """
    Data queries resolving organization user memberships.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OrganizationMember, session=session)

    async def get_member(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMember | None:
        """
        Retrieve specific membership mapping between organization and user.
        """
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_org_id(self, organization_id: uuid.UUID) -> list[OrganizationMember]:
        """
        Retrieve all member mappings belonging to an organization.
        """
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[OrganizationMember]:
        """
        Retrieve all organization memberships held by a user.
        """
        query = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def remove_member(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete membership mapping.
        """
        stmt = delete(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return True


class OrganizationInvitationRepository(BaseRepository[OrganizationInvitation]):
    """
    Data queries for managing pending and accepted registration invites.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OrganizationInvitation, session=session)

    async def get_by_token(self, token: str) -> OrganizationInvitation | None:
        """
        Resolve an invitation record by secure invite token.
        """
        query = select(OrganizationInvitation).where(
            OrganizationInvitation.token == token
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_by_org_id(self, organization_id: uuid.UUID) -> list[OrganizationInvitation]:
        """
        List all invitations currently awaiting action in a tenant organization.
        """
        query = select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.status == "pending"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_by_email(self, email: str) -> list[OrganizationInvitation]:
        """
        Resolve active invitations matching a recipient email.
        """
        query = select(OrganizationInvitation).where(
            OrganizationInvitation.email == email.lower(),
            OrganizationInvitation.status == "pending"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
