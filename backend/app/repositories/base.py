"""
Nexora Platform — Base Repository Implementation

Concrete SQLAlchemy implementation of the IRepository interface.
Provides async CRUD operations with multi-tenant scoping and soft delete.

All queries automatically filter by organization_id and is_deleted=False
to enforce tenant isolation and soft delete semantics.

Usage:
    class UserRepository(BaseRepository[User]):
        def __init__(self, session: AsyncSession):
            super().__init__(model=User, session=session)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging import get_logger
from app.core.interfaces.repository import IRepository
from app.models.base import BaseModel

# Type variable bound to BaseModel so we get type safety
ModelT = TypeVar("ModelT", bound=BaseModel)

logger = get_logger(__name__)


class BaseRepository(IRepository[ModelT], Generic[ModelT]):
    """
    Generic SQLAlchemy repository implementing IRepository.

    Provides standard CRUD operations for any model extending BaseModel.
    All queries are organization-scoped and respect soft delete.

    Type Parameters:
        ModelT: The SQLAlchemy model class this repository manages.

    Attributes:
        model: The SQLAlchemy model class.
        session: The async database session.
    """

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            model: The SQLAlchemy model class.
            session: An async database session.
        """
        self.model = model
        self.session = session

    def _base_query(self, organization_id: UUID) -> Select[tuple[ModelT]]:
        """
        Create a base query scoped to an organization with soft delete filter.

        Args:
            organization_id: UUID of the organization.

        Returns:
            A select query with organization and soft delete filters applied.
        """
        return (
            select(self.model)
            .where(self.model.organization_id == organization_id)
            .where(self.model.is_deleted == False)  # noqa: E712
        )

    async def get_by_id(self, entity_id: UUID, organization_id: UUID) -> ModelT | None:
        """Retrieve a single entity by ID within an organization."""
        query = self._base_query(organization_id).where(self.model.id == entity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelT]:
        """Retrieve a paginated list of entities within an organization."""
        query = self._base_query(organization_id)

        # Apply dynamic filters
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name) and value is not None:
                    query = query.where(getattr(self.model, field_name) == value)

        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        organization_id: UUID,
        *,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """Count entities within an organization."""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.organization_id == organization_id)
            .where(self.model.is_deleted == False)  # noqa: E712
        )

        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name) and value is not None:
                    query = query.where(getattr(self.model, field_name) == value)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        logger.info(
            "entity_created",
            model=self.model.__name__,
            entity_id=str(entity.id),
            organization_id=str(entity.organization_id),
        )
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """Update an existing entity."""
        entity.updated_at = datetime.now(tz=timezone.utc)
        await self.session.flush()
        await self.session.refresh(entity)
        logger.info(
            "entity_updated",
            model=self.model.__name__,
            entity_id=str(entity.id),
            organization_id=str(entity.organization_id),
        )
        return entity

    async def soft_delete(self, entity_id: UUID, organization_id: UUID) -> bool:
        """Soft delete an entity by setting is_deleted=True."""
        entity = await self.get_by_id(entity_id, organization_id)
        if entity is None:
            return False

        entity.is_deleted = True
        entity.deleted_at = datetime.now(tz=timezone.utc)
        await self.session.flush()

        logger.info(
            "entity_soft_deleted",
            model=self.model.__name__,
            entity_id=str(entity_id),
            organization_id=str(organization_id),
        )
        return True

    async def hard_delete(self, entity_id: UUID, organization_id: UUID) -> bool:
        """Permanently delete an entity from the database."""
        entity = await self.get_by_id(entity_id, organization_id)
        if entity is None:
            return False

        await self.session.delete(entity)
        await self.session.flush()

        logger.warning(
            "entity_hard_deleted",
            model=self.model.__name__,
            entity_id=str(entity_id),
            organization_id=str(organization_id),
        )
        return True
