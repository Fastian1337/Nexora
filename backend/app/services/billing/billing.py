"""
Nexora Platform — Billing & Subscription Lifecycle Service
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from redis.asyncio import Redis
from sqlalchemy import select

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.billing import (
    Plan,
    Subscription,
    Invoice,
    Payment,
    PaymentMethod,
    UsageRecord,
    Coupon,
    Discount,
    Transaction,
    Refund,
)
from app.repositories.billing import (
    PlanRepository,
    SubscriptionRepository,
    InvoiceRepository,
    PaymentRepository,
    PaymentMethodRepository,
    UsageRecordRepository,
    CouponRepository,
    DiscountRepository,
    TransactionRepository,
    RefundRepository,
)
from app.services.billing.gateway import StripeProvider, JazzCashProvider, EasyPaisaProvider
from app.config.logging import get_logger

logger = get_logger(__name__)


class BillingService:
    """
    Business service managing recurring SaaS plans, usage trackers, invoicing, and gateways.
    """

    def __init__(
        self,
        plan_repo: PlanRepository,
        sub_repo: SubscriptionRepository,
        invoice_repo: InvoiceRepository,
        payment_repo: PaymentRepository,
        pm_repo: PaymentMethodRepository,
        usage_repo: UsageRecordRepository,
        coupon_repo: CouponRepository,
        discount_repo: DiscountRepository,
        tx_repo: TransactionRepository,
        refund_repo: RefundRepository,
        redis: Redis,
    ) -> None:
        self.plan_repo = plan_repo
        self.sub_repo = sub_repo
        self.invoice_repo = invoice_repo
        self.payment_repo = payment_repo
        self.pm_repo = pm_repo
        self.usage_repo = usage_repo
        self.coupon_repo = coupon_repo
        self.discount_repo = discount_repo
        self.tx_repo = tx_repo
        self.refund_repo = refund_repo
        self.redis = redis

    def _get_gateway(self, provider: str) -> Any:
        provider_lower = provider.lower().strip()
        if provider_lower == "stripe":
            return StripeProvider()
        elif provider_lower == "jazzcash":
            return JazzCashProvider()
        elif provider_lower == "easypaisa":
            return EasyPaisaProvider()
        else:
            raise ValidationException(
                message=f"Unsupported billing provider: {provider}",
                error_code="UNSUPPORTED_PROVIDER",
            )

    async def get_active_subscription(self, organization_id: uuid.UUID) -> Subscription | None:
        """Fetch subscription details, checking Redis cache first."""
        cache_key = f"org:subscription:{organization_id}"
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                # Query DB to return actual SQLAlchemy object if needed, but returning directly is faster
        except Exception as e:
            logger.warning("subscription_cache_lookup_failed", error=str(e))

        sub = await self.sub_repo.get_by_org_id(organization_id)
        if sub:
            # Write cache
            try:
                sub_data = {
                    "id": str(sub.id),
                    "plan_code": sub.plan.code,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end.isoformat(),
                }
                await self.redis.setex(cache_key, 1800, json.dumps(sub_data))
            except Exception as e:
                logger.warning("subscription_cache_write_failed", error=str(e))
        return sub

    async def clear_subscription_cache(self, organization_id: uuid.UUID) -> None:
        cache_key = f"org:subscription:{organization_id}"
        try:
            await self.redis.delete(cache_key)
        except Exception as e:
            logger.warning("subscription_cache_clear_failed", error=str(e))

    async def checkout_subscription(
        self,
        organization_id: uuid.UUID,
        plan_code: str,
        provider: str,
        payment_token: str,
        coupon_code: str | None = None,
    ) -> Subscription:
        """
        Processes checkout, runs merchant gateway charges, applies coupons,
        registers subscriptions, and logs paid invoices.
        """
        # 1. Fetch Plan
        plan = await self.plan_repo.get_by_code(plan_code)
        if not plan:
            raise NotFoundException(message="Selected billing plan not found", error_code="PLAN_NOT_FOUND")

        # 2. Check current subscription
        existing_sub = await self.sub_repo.get_by_org_id(organization_id)
        if existing_sub and existing_sub.status in ["active", "trialing"]:
            # Downgrade or upgrade - clear existing discounts first
            await self.sub_repo.delete(existing_sub.id, organization_id)

        # 3. Apply Coupons
        original_amount = plan.price_cents
        discount_amount = 0
        coupon = None
        if coupon_code:
            coupon = await self.coupon_repo.get_by_code(coupon_code)
            if coupon:
                if coupon.discount_type == "percentage":
                    discount_amount = int((original_amount * coupon.discount_value) / 100)
                else:
                    discount_amount = coupon.discount_value
                coupon.usages_count += 1
                await self.coupon_repo.update(coupon)

        charge_amount = max(0, original_amount - discount_amount)

        # 4. Process charge via gateway
        gateway = self._get_gateway(provider)
        charge_result = {"success": True, "transaction_id": f"mock_tx_{uuid.uuid4().hex[:12]}"}
        if charge_amount > 0:
            charge_result = await gateway.charge(
                customer_id=f"cus_{organization_id.hex[:10]}",
                amount_cents=charge_amount,
                currency=plan.currency,
                payment_method_token=payment_token,
            )

        # 5. Create Subscription
        now = datetime.now(timezone.utc)
        sub = Subscription(
            organization_id=organization_id,
            plan_id=plan.id,
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            cancel_at_period_end=False,
        )
        created_sub = await self.sub_repo.create(sub)

        # Apply Discount model entry
        if coupon:
            discount = Discount(
                organization_id=organization_id,
                subscription_id=created_sub.id,
                coupon_id=coupon.id,
                amount_cents=discount_amount,
            )
            await self.discount_repo.create(discount)

        # 6. Generate Invoice
        invoice = Invoice(
            organization_id=organization_id,
            invoice_number=f"INV-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}",
            subscription_id=created_sub.id,
            amount_cents=charge_amount,
            tax_cents=0,
            currency=plan.currency,
            status="paid",
            period_start=now,
            period_end=now + timedelta(days=30),
            due_at=now,
            paid_at=now,
        )
        created_invoice = await self.invoice_repo.create(invoice)

        # 7. Record Payment Methods & Payments
        pm = PaymentMethod(
            organization_id=organization_id,
            provider=provider,
            provider_payment_method_id=payment_token,
            brand="Visa",
            last_digits="4242",
            is_default=True,
            status="active",
        )
        created_pm = await self.pm_repo.create(pm)

        payment_log = Payment(
            organization_id=organization_id,
            invoice_id=created_invoice.id,
            payment_method_id=created_pm.id,
            amount_cents=charge_amount,
            currency=plan.currency,
            status="succeeded",
            provider=provider,
            transaction_id=charge_result.get("transaction_id"),
        )
        await self.payment_repo.create(payment_log)

        # 8. Log Transaction Ledger
        tx = Transaction(
            organization_id=organization_id,
            type="charge",
            amount_cents=charge_amount,
            currency=plan.currency,
            description=f"Subscription charge for {plan.name} plan",
        )
        await self.tx_repo.create(tx)

        await self.clear_subscription_cache(organization_id)
        logger.info("subscription_checkout_succeeded", org_id=str(organization_id), plan=plan_code)
        return created_sub

    async def cancel_subscription(self, organization_id: uuid.UUID) -> Subscription:
        """Cancel subscription mapping at the end of the active billing period."""
        sub = await self.sub_repo.get_by_org_id(organization_id)
        if not sub:
            raise NotFoundException(message="Active subscription not found", error_code="SUBSCRIPTION_NOT_FOUND")

        sub.cancel_at_period_end = True
        sub.status = "cancelled"
        updated = await self.sub_repo.update(sub)
        await self.clear_subscription_cache(organization_id)
        return updated

    async def increment_usage(self, organization_id: uuid.UUID, metric_name: str, quantity: int = 1) -> UsageRecord:
        """Increment usage telemetry for an organization."""
        record = await self.usage_repo.get_usage_by_metric(organization_id, metric_name)
        now = datetime.now(timezone.utc)
        if not record:
            record = UsageRecord(
                organization_id=organization_id,
                metric_name=metric_name.lower().strip(),
                quantity=quantity,
                reset_at=now + timedelta(days=30),
            )
            created = await self.usage_repo.create(record)
            return created

        record.quantity += quantity
        updated = await self.usage_repo.update(record)
        return updated

    async def reset_monthly_usage(self, organization_id: uuid.UUID) -> None:
        """Reset usage counts back to zero."""
        query = select(UsageRecord).where(UsageRecord.organization_id == organization_id)
        result = await self.usage_repo.session.execute(query)
        records = result.scalars().all()
        now = datetime.now(timezone.utc)
        for r in records:
            r.quantity = 0
            r.reset_at = now + timedelta(days=30)
            await self.usage_repo.update(r)
        logger.info("monthly_usage_reset_succeeded", org_id=str(organization_id))

    async def seed_default_plans(self) -> None:
        """Seed default Plans into database."""
        default_plans = [
            ("Free Plan", "free", "Sandbox testing tier", 0, "USD", "monthly", {
                "max_users": 2,
                "max_agents": 1,
                "voice_enabled": False,
                "whatsapp_enabled": False,
                "analytics_enabled": False,
                "custom_branding": False,
                "api_calls_limit": 500,
                "storage_limit_mb": 50,
            }),
            ("Starter Plan", "starter", "Great for small clinic or retail workspace", 2900, "USD", "monthly", {
                "max_users": 5,
                "max_agents": 3,
                "voice_enabled": True,
                "whatsapp_enabled": False,
                "analytics_enabled": True,
                "custom_branding": False,
                "api_calls_limit": 5000,
                "storage_limit_mb": 500,
            }),
            ("Professional Plan", "professional", "Production standard tier", 7900, "USD", "monthly", {
                "max_users": 20,
                "max_agents": 10,
                "voice_enabled": True,
                "whatsapp_enabled": True,
                "analytics_enabled": True,
                "custom_branding": True,
                "api_calls_limit": 50000,
                "storage_limit_mb": 5000,
            }),
            ("Business Plan", "business", "Advanced automation and custom domains", 19900, "USD", "monthly", {
                "max_users": 50,
                "max_agents": 25,
                "voice_enabled": True,
                "whatsapp_enabled": True,
                "analytics_enabled": True,
                "custom_branding": True,
                "api_calls_limit": 200000,
                "storage_limit_mb": 20000,
            }),
            ("Enterprise Plan", "enterprise", "Unlimited parameters scoped for large companies", 99900, "USD", "monthly", {
                "max_users": 9999,
                "max_agents": 999,
                "voice_enabled": True,
                "whatsapp_enabled": True,
                "analytics_enabled": True,
                "custom_branding": True,
                "api_calls_limit": 9999999,
                "storage_limit_mb": 1000000,
            }),
        ]

        for name, code, desc, price, curr, interval, feats in default_plans:
            existing = await self.plan_repo.get_by_code(code)
            if not existing:
                plan = Plan(
                    name=name,
                    code=code,
                    description=desc,
                    price_cents=price,
                    currency=curr,
                    billing_interval=interval,
                    features=feats,
                )
                await self.plan_repo.create(plan)
            else:
                existing.features = feats
                existing.price_cents = price
                await self.plan_repo.update(existing)
