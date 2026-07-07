"""
Nexora Platform — Base Repository Interface

Defines the abstract contract that all repository implementations must follow.
This is a Domain layer interface — it knows nothing about SQLAlchemy or
any specific database technology.

The infrastructure layer (app/repositories/) provides concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

# Generic type variable for entity models
T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Abstract base repository interface.

    Defines the standard CRUD contract for data access.
    All methods are organization-scoped to enforce multi-tenancy.

    Type Parameters:
        T: The entity type this repository manages.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: UUID, organization_id: UUID) -> T | None:
        """
        Retrieve a single entity by its ID within an organization.

        Args:
            entity_id: UUID of the entity to retrieve.
            organization_id: UUID of the organization (tenant scope).

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        """
        Retrieve a paginated list of entities within an organization.

        Args:
            organization_id: UUID of the organization (tenant scope).
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            filters: Optional key-value filters to apply.

        Returns:
            List of entities matching the criteria.
        """
        ...

    @abstractmethod
    async def count(
        self,
        organization_id: UUID,
        *,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Count entities within an organization.

        Args:
            organization_id: UUID of the organization (tenant scope).
            filters: Optional key-value filters to apply.

        Returns:
            Total count of matching entities.
        """
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Persist a new entity.

        Args:
            entity: The entity to create.

        Returns:
            The created entity with generated fields (id, timestamps).
        """
        ...

    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Update an existing entity.

        Args:
            entity: The entity with updated fields.

        Returns:
            The updated entity.
        """
        ...

    @abstractmethod
    async def soft_delete(self, entity_id: UUID, organization_id: UUID) -> bool:
        """
        Soft delete an entity (set is_deleted=True, deleted_at=now).

        Args:
            entity_id: UUID of the entity to delete.
            organization_id: UUID of the organization (tenant scope).

        Returns:
            True if the entity was found and deleted, False otherwise.
        """
        ...

    @abstractmethod
    async def hard_delete(self, entity_id: UUID, organization_id: UUID) -> bool:
        """
        Permanently delete an entity from the database.

        Use with extreme caution — this cannot be undone.

        Args:
            entity_id: UUID of the entity to delete.
            organization_id: UUID of the organization (tenant scope).

        Returns:
            True if the entity was found and deleted, False otherwise.
        """
        ...
