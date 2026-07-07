"""
Nexora Platform — Billing & Subscriptions ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel


class Plan(Base):
    """
    Global Billing Plans table.
    Defines subscription packages, price point, and limits.
    """

    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    billing_interval: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")
    features: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

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
    subscriptions: Mapped[list[Subscription]] = relationship("Subscription", back_populates="plan")

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, code={self.code})>"


class Subscription(BaseModel):
    """
    Tenant Subscriptions table.
    Links organizations to a specific active billing Plan.
    """

    __tablename__ = "subscriptions"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="subscription")
    plan: Mapped[Plan] = relationship("Plan", back_populates="subscriptions")

    # Override organization_id to be unique (one subscription per organization)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, org={self.organization_id}, status={self.status})>"
