"""
Nexora Platform — System Configuration & Files ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel


class Organization(Base):
    """
    Core Tenant Model.
    Stores the business or organization information acting as the tenant.
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    users: Mapped[list[User]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    roles: Mapped[list[Role]] = relationship("Role", back_populates="organization", cascade="all, delete-orphan")
    subscription: Mapped[Subscription | None] = relationship("Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, slug={self.slug})>"


class File(BaseModel):
    """
    Files Metadata Model.
    Tracks files uploaded to the S3-compatible object storage per tenant.
    """

    __tablename__ = "files"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename={self.filename})>"


class SystemSettings(Base):
    """
    Global Platform-wide configuration settings.
    """

    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SystemSettings(id={self.id}, key={self.key})>"
