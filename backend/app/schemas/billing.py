"""
Nexora Platform — Billing Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.base import BaseSchema


class PlanResponse(BaseSchema):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    price_cents: int
    currency: str
    billing_interval: str
    features: dict[str, Any]


class SubscriptionResponse(BaseSchema):
    id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    plan: PlanResponse


class SubscriptionCheckoutRequest(BaseSchema):
    plan_code: str = Field(min_length=2, max_length=50)
    provider: str = Field(min_length=3, max_length=50)  # stripe, jazzcash, easypaisa
    payment_token: str = Field(min_length=2, max_length=255)
    coupon_code: str | None = Field(default=None, max_length=50)


class InvoiceResponse(BaseSchema):
    id: uuid.UUID
    invoice_number: str
    amount_cents: int
    tax_cents: int
    currency: str
    status: str
    pdf_url: str | None
    period_start: datetime
    period_end: datetime
    due_at: datetime
    paid_at: datetime | None


class UsageRecordResponse(BaseSchema):
    id: uuid.UUID
    metric_name: str
    quantity: int
    reset_at: datetime


class CouponCreate(BaseSchema):
    code: str = Field(min_length=3, max_length=50, pattern=r"^[A-Z0-9_]+$")
    discount_type: str = Field(default="percentage", pattern=r"^(percentage|fixed)$")
    discount_value: int = Field(gt=0)
    expires_at: datetime | None = None
    max_usages: int | None = None


class CouponResponse(BaseSchema):
    id: uuid.UUID
    code: str
    discount_type: str
    discount_value: int
    currency: str
    expires_at: datetime | None
    is_active: bool
