"""
Nexora Platform — User & Authentication ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Uuid, Table, Column, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

# Join Table: Role Permissions (Many-to-Many join table)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Uuid(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Join Table: User Roles (Many-to-Many join table with organization_id audit)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("organization_id", Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
)


class Permission(Base):
    """
    Global Permission Registry.
    Defines capabilities such as 'agent:write' or 'conversation:read'.
    """

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code={self.code})>"


class Role(BaseModel):
    """
    Tenant-specific Roles table.
    Enables Role-Based Access Control (RBAC).
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="roles")
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )
    users: Mapped[list[User]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, org={self.organization_id})>"


class User(BaseModel):
    """
    Users Directory.
    Tracks authentication and identity for users.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    account_locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="users")
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
