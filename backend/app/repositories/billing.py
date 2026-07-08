"""
Nexora Platform — Billing Data Access Repositories
"""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.billing import (
    Plan,
    Subscription,
    Invoice,
    Payment,
    PaymentMethod,
    UsageRecord,
    Coupon,
    Discount,
    Credit,
    Transaction,
    Refund,
    BillingAddress,
    TaxSetting,
    OrganizationLicense,
)
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Plan, session=session)

    async def get_by_code(self, code: str) -> Plan | None:
        query = select(Plan).where(Plan.code == code.lower().strip())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Subscription, session=session)

    async def get_by_org_id(self, organization_id: uuid.UUID) -> Subscription | None:
        query = select(Subscription).where(
            Subscription.organization_id == organization_id
        ).options(selectinload(Subscription.plan))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Invoice, session=session)

    async def get_by_number(self, invoice_number: str) -> Invoice | None:
        query = select(Invoice).where(Invoice.invoice_number == invoice_number.strip())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_org_id(self, organization_id: uuid.UUID) -> list[Invoice]:
        query = select(Invoice).where(Invoice.organization_id == organization_id).order_by(Invoice.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Payment, session=session)


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=PaymentMethod, session=session)

    async def get_default_by_org_id(self, organization_id: uuid.UUID) -> PaymentMethod | None:
        query = select(PaymentMethod).where(
            PaymentMethod.organization_id == organization_id,
            PaymentMethod.is_default == True,  # noqa: E712
            PaymentMethod.status == "active"
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class UsageRecordRepository(BaseRepository[UsageRecord]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=UsageRecord, session=session)

    async def get_usage_by_metric(self, organization_id: uuid.UUID, metric_name: str) -> UsageRecord | None:
        query = select(UsageRecord).where(
            UsageRecord.organization_id == organization_id,
            UsageRecord.metric_name == metric_name.lower().strip()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class CouponRepository(BaseRepository[Coupon]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Coupon, session=session)

    async def get_by_code(self, code: str) -> Coupon | None:
        query = select(Coupon).where(
            Coupon.code == code.upper().strip(),
            Coupon.is_active == True  # noqa: E712
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DiscountRepository(BaseRepository[Discount]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Discount, session=session)


class CreditRepository(BaseRepository[Credit]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Credit, session=session)


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Transaction, session=session)


class RefundRepository(BaseRepository[Refund]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Refund, session=session)


class BillingAddressRepository(BaseRepository[BillingAddress]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=BillingAddress, session=session)


class TaxSettingRepository(BaseRepository[TaxSetting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=TaxSetting, session=session)


class OrganizationLicenseRepository(BaseRepository[OrganizationLicense]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OrganizationLicense, session=session)
