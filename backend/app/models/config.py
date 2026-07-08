"""
Nexora Platform — System Configuration, Tenants, settings & Invitations ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func, Integer
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

    # Expanded metadata
    business_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    brand_colors: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

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
    users: Mapped[list[User]] = relationship("User", back_populates="organization", foreign_keys="[User.organization_id]")
    roles: Mapped[list[Role]] = relationship("Role", back_populates="organization", cascade="all, delete-orphan")
    subscription: Mapped[Subscription | None] = relationship("Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    settings: Mapped[OrganizationSettings | None] = relationship("OrganizationSettings", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    members: Mapped[list[OrganizationMember]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invitations: Mapped[list[OrganizationInvitation]] = relationship("OrganizationInvitation", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, slug={self.slug})>"


class OrganizationSettings(Base):
    """
    Branding & Configurations settings scoped specifically per Organization.
    """

    __tablename__ = "organization_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    theme: Mapped[str | None] = mapped_column(String(50), nullable=True, default="dark")
    brand_colors: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    business_hours: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    working_days: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    languages: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    voice_language: Mapped[str | None] = mapped_column(String(50), nullable=True, default="en")
    ai_personality: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notification_preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    whatsapp_settings: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    email_settings: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    social_media_accounts: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)

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

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="settings")


class OrganizationMember(Base):
    """
    Association Table tracking memberships and user roles inside multiple Organizations.
    """

    __tablename__ = "organization_members"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee", index=True)  # owner, admin, manager, employee, receptionist, doctor, teacher, marketing_manager, sales

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

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="memberships", foreign_keys="[OrganizationMember.user_id]")


class OrganizationInvitation(Base):
    """
    Tracks self-serve team registration tokens sent to user email addresses.
    """

    __tablename__ = "organization_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee")
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)  # pending, accepted, rejected, expired
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

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

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="invitations")
    inviter: Mapped[User] = relationship("User", foreign_keys="[OrganizationInvitation.invited_by]")


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
