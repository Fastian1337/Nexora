"""
Nexora Platform — Base SQLAlchemy Model

Provides the declarative base and a base model class that all
domain entity models must inherit from. Ensures consistent:

- UUID primary keys
- Organization scoping (multi-tenancy)
- Timestamps (created_at, updated_at)
- Soft delete (is_deleted, deleted_at)
- Audit fields (created_by, updated_by)

Usage:
    from app.models.base import BaseModel

    class User(BaseModel):
        __tablename__ = "users"

        email = mapped_column(String(255), nullable=False, unique=True)
        name = mapped_column(String(255), nullable=False)
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Uuid, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.

    All ORM models must inherit from this base (via BaseModel).
    This class is used by Alembic for auto-detecting model changes.
    """

    pass


class BaseModel(Base):
    """
    Abstract base model with standard fields for all Nexora entities.

    Provides:
        - id: UUID primary key (auto-generated)
        - organization_id: UUID for multi-tenant scoping
        - created_at: Timestamp of creation (server-side default)
        - updated_at: Timestamp of last update (auto-updated)
        - is_deleted: Soft delete flag
        - deleted_at: Timestamp of soft deletion
        - created_by: UUID of the user who created the entity
        - updated_by: UUID of the user who last updated the entity

    All concrete models inherit these fields automatically.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
        comment="Organization (tenant) that owns this record",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the record was last updated",
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
        comment="Soft delete flag — true means the record is logically deleted",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the record was soft deleted",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        default=None,
        comment="UUID of the user who created this record",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        default=None,
        comment="UUID of the user who last updated this record",
    )

    @declared_attr
    def __table_args__(cls) -> tuple[Any, ...]:
        return (
            Index(
                f"ix_{cls.__tablename__}_org_not_deleted",
                "organization_id",
                "is_deleted",
            ),
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, org={self.organization_id})>"

    def soft_delete(self) -> None:
        """Mark this entity as soft-deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(tz=None)  # Will be timezone-aware via DB
