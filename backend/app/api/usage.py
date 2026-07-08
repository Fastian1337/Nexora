"""
Nexora Platform — Usage Limits Validation Middleware

FastAPI dependencies to verify active subscriptions, enabled feature keys,
and organization quota limits before running premium features.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_organization
from app.core.exceptions import ValidationException
from app.db.session import get_db_session
from app.models.user import User
from app.models.config import Organization


class RequireUsageLimit:
    """
    Enforces subscription state, custom feature flags, and numeric usage quotas.
    """

    def __init__(self, metric_name: str, limit_key: str | None = None) -> None:
        self.metric_name = metric_name
        self.limit_key = limit_key or f"{metric_name}_limit"

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        active_org: Organization = Depends(get_current_organization),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        from app.db.redis import get_redis_client
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
        from app.services.billing.billing import BillingService

        redis_client = get_redis_client()
        sub_repo = SubscriptionRepository(session=db)
        plan_repo = PlanRepository(session=db)
        usage_repo = UsageRecordRepository(session=db)
        
        # Instantiate BillingService
        billing_service = BillingService(
            plan_repo=plan_repo,
            sub_repo=sub_repo,
            invoice_repo=InvoiceRepository(session=db),
            payment_repo=PaymentRepository(session=db),
            pm_repo=PaymentMethodRepository(session=db),
            usage_repo=usage_repo,
            coupon_repo=CouponRepository(session=db),
            discount_repo=DiscountRepository(session=db),
            tx_repo=TransactionRepository(session=db),
            refund_repo=RefundRepository(session=db),
            redis=redis_client,
        )

        # 1. Resolve Subscription
        sub = await billing_service.get_active_subscription(active_org.id)
        if not sub or sub.status not in ["active", "trialing", "grace_period"]:
            raise ValidationException(
                message="Subscription is inactive or expired. Please checkout a subscription plan to access this feature.",
                error_code="INACTIVE_SUBSCRIPTION",
            )

        # 2. Check Feature Flag Enablement (if metric_name resolves as a feature flag)
        plan = sub.plan
        features = plan.features or {}
        
        # If the metric name itself ends with _enabled or is configured as a boolean flag
        feature_flag_key = f"{self.metric_name}_enabled"
        if feature_flag_key in features:
            if not features.get(feature_flag_key, False):
                raise ValidationException(
                    message=f"Feature '{self.metric_name}' is not enabled on your current {plan.name} plan.",
                    error_code="FEATURE_DISABLED",
                )

        # 3. Check Numeric Limits (e.g. max_users, storage_limit_mb, etc.)
        limit_val = features.get(self.limit_key)
        if limit_val is not None:
            # Query active usage record
            record = await usage_repo.get_usage_by_metric(active_org.id, self.metric_name)
            current_qty = record.quantity if record else 0
            
            if current_qty >= limit_val:
                raise ValidationException(
                    message=f"Usage limit reached: you have consumed {current_qty}/{limit_val} units of '{self.metric_name}' on your current plan.",
                    error_code="USAGE_LIMIT_EXCEEDED",
                )
