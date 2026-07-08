"""
Nexora Platform — Billing & Subscriptions API Router Endpoints
"""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select

from app.api.deps import get_billing_service, get_current_user, get_current_organization
from app.api.authorization import RequireAdmin
from app.models.user import User
from app.models.config import Organization
from app.models.billing import Plan, Coupon, UsageRecord
from app.schemas.base import ApiResponse
from app.schemas.billing import (
    PlanResponse,
    SubscriptionResponse,
    SubscriptionCheckoutRequest,
    InvoiceResponse,
    UsageRecordResponse,
    CouponCreate,
    CouponResponse,
)
from app.services.billing.billing import BillingService

router = APIRouter(prefix="/billing", tags=["Billing & Subscriptions"])


@router.get(
    "/plans",
    response_model=ApiResponse[list[PlanResponse]],
    status_code=status.HTTP_200_OK,
    summary="List default subscription packages",
)
async def list_plans(
    request: Request,
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Returns pricing configuration packages and their limits.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    # Query default seeded plans
    query = select(Plan).order_by(Plan.price_cents)
    result = await billing_service.plan_repo.session.execute(query)
    plans = result.scalars().all()

    data = [PlanResponse.model_validate(p) for p in plans]
    return {
        "success": True,
        "message": "Plans retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/subscription/me",
    response_model=ApiResponse[SubscriptionResponse | None],
    status_code=status.HTTP_200_OK,
    summary="Get current organization subscription details",
)
async def get_my_subscription(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Retrieves subscription limits, status, and active plan detail context.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    sub = await billing_service.get_active_subscription(active_org.id)
    
    data = SubscriptionResponse.model_validate(sub) if sub else None
    return {
        "success": True,
        "message": "Active subscription details retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/subscription/checkout",
    response_model=ApiResponse[SubscriptionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Checkout organization billing plan",
)
async def checkout_subscription(
    payload: SubscriptionCheckoutRequest,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Checkout active pricing package, running billing charge operations.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    sub = await billing_service.checkout_subscription(
        organization_id=active_org.id,
        plan_code=payload.plan_code,
        provider=payload.provider,
        payment_token=payload.payment_token,
        coupon_code=payload.coupon_code,
    )

    data = SubscriptionResponse.model_validate(sub)
    return {
        "success": True,
        "message": "Subscription checked out successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/subscription/cancel",
    response_model=ApiResponse[SubscriptionResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel active organization subscription",
)
async def cancel_subscription(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Flags active subscription to cancel at period end.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    sub = await billing_service.cancel_subscription(active_org.id)
    data = SubscriptionResponse.model_validate(sub)
    return {
        "success": True,
        "message": "Subscription cancellation scheduled",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/invoices",
    response_model=ApiResponse[list[InvoiceResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get invoice payment history",
)
async def list_invoices(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Returns chronological invoice history list.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    invoices = await billing_service.invoice_repo.list_by_org_id(active_org.id)
    data = [InvoiceResponse.model_validate(inv) for inv in invoices]
    return {
        "success": True,
        "message": "Invoice lists retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/usage",
    response_model=ApiResponse[list[UsageRecordResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get usage telemetry tracker",
)
async def get_usage_telemetry(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Get organization's consumed metrics quotas.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    query = select(UsageRecord).where(UsageRecord.organization_id == active_org.id)
    result = await billing_service.usage_repo.session.execute(query)
    records = result.scalars().all()
    
    data = [UsageRecordResponse.model_validate(r) for r in records]
    return {
        "success": True,
        "message": "Usage metrics retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/coupons",
    response_model=ApiResponse[CouponResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireAdmin())],
    summary="Create coupon codes",
)
async def create_coupon(
    payload: CouponCreate,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    billing_service: BillingService = Depends(get_billing_service),
) -> dict:
    """
    Registers custom campaign coupon code. (Admin only).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    coupon = Coupon(
        organization_id=active_org.id,
        code=payload.code.upper().strip(),
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        expires_at=payload.expires_at,
        max_usages=payload.max_usages,
        usages_count=0,
        is_active=True,
    )
    created = await billing_service.coupon_repo.create(coupon)
    data = CouponResponse.model_validate(created)
    return {
        "success": True,
        "message": "Coupon registered successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/webhook/{provider}",
    status_code=status.HTTP_200_OK,
    summary="Gateway webhook processor",
)
async def webhook_handler(
    provider: str,
    payload: dict[str, Any],
) -> dict:
    """
    Webhook handler processing billing event signals.
    """
    logger.info("webhook_received", provider=provider, event=payload.get("type"))
    return {"success": True, "message": "Webhook processed successfully"}
