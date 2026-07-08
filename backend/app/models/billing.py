"""
Nexora Platform — Billing, Plans, Subscriptions, Invoices & Usage ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func, Integer, Float
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
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # free, starter, professional, business, enterprise
    description: Mapped[str | None] = mapped_column(nullable=True)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    billing_interval: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")  # monthly, yearly
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
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)  # active, trialing, paused, cancelled, expired, grace_period
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trial_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Override organization_id to be unique (one subscription per organization)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="subscription", foreign_keys="[Subscription.organization_id]")
    plan: Mapped[Plan] = relationship("Plan", back_populates="subscriptions")
    invoices: Mapped[list[Invoice]] = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    discounts: Mapped[list[Discount]] = relationship("Discount", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, org={self.organization_id}, status={self.status})>"


class Invoice(BaseModel):
    """
    Invoice records generated automatically per organization tenant.
    """

    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    tax_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unpaid", index=True)  # paid, unpaid, draft, void
    pdf_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscription: Mapped[Subscription] = relationship("Subscription", back_populates="invoices")
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class PaymentMethod(BaseModel):
    """
    Secure references to tokens from supported providers.
    """

    __tablename__ = "payment_methods"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # stripe, jazzcash, easypaisa
    provider_payment_method_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_digits: Mapped[str | None] = mapped_column(String(10), nullable=True)
    exp_month: Mapped[int | None] = mapped_column(nullable=True)
    exp_year: Mapped[int | None] = mapped_column(nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="payment_method")


class Payment(BaseModel):
    """
    Billing charges mapped to invoices.
    """

    __tablename__ = "payments"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_method_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing", index=True)  # succeeded, failed, processing
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Relationships
    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="payments")
    payment_method: Mapped[PaymentMethod | None] = relationship("PaymentMethod", back_populates="payments")
    refunds: Mapped[list[Refund]] = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")


class UsageRecord(BaseModel):
    """
    Usage telemetry log records per tenant organization.
    """

    __tablename__ = "usage_records"

    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # ai_requests, voice_minutes, messages, storage_bytes
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Coupon(BaseModel):
    """
    Campaign discount codes. Can be restricted to specific organization.
    """

    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False, default="percentage")  # percentage, fixed
    discount_value: Mapped[int] = mapped_column(nullable=False)  # fixed cents or percentage integer (e.g. 20 for 20%)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_usages: Mapped[int | None] = mapped_column(nullable=True)
    usages_count: Mapped[int] = mapped_column(nullable=False, default=0)
    target_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    discounts: Mapped[list[Discount]] = relationship("Discount", back_populates="coupon")


class Discount(BaseModel):
    """
    Record of coupon allocations on subscriptions.
    """

    __tablename__ = "discounts"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coupon_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_cents: Mapped[int] = mapped_column(nullable=False)

    # Relationships
    subscription: Mapped[Subscription] = relationship("Subscription", back_populates="discounts")
    coupon: Mapped[Coupon] = relationship("Coupon", back_populates="discounts")


class Credit(BaseModel):
    """
    Credits held by organization balance sheets.
    """

    __tablename__ = "credits"

    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Transaction(BaseModel):
    """
    General ledger auditing cash, credits, and adjustments.
    """

    __tablename__ = "transactions"

    type: Mapped[str] = mapped_column(String(50), nullable=False)  # charge, refund, credit_add, credit_use
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Refund(BaseModel):
    """
    Tracks transaction refunding transactions.
    """

    __tablename__ = "refunds"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="succeeded")  # succeeded, failed

    # Relationships
    payment: Mapped[Payment] = relationship("Payment", back_populates="refunds")


class BillingAddress(BaseModel):
    """
    Official client organization billing locations.
    """

    __tablename__ = "billing_addresses"

    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)


class TaxSetting(BaseModel):
    """
    Tax rates and organization registers.
    """

    __tablename__ = "tax_settings"

    tax_id_type: Mapped[str] = mapped_column(String(50), nullable=False)  # VAT, GST, TIN
    tax_id_number: Mapped[str] = mapped_column(String(100), nullable=False)
    rate_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class OrganizationLicense(BaseModel):
    """
    License keys issued for offline or enterprise client distributions.
    """

    __tablename__ = "organization_licenses"

    license_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_organizations: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
