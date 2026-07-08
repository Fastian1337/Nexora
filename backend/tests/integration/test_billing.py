"""
Nexora Platform — Billing & Subscription Integration Tests

Validates billing plans listings, checkout pipelines, invoice listings,
usage tracker progress metrics, and usage limitations middleware blocks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient

from app.api.deps import get_billing_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.billing import Plan, Subscription, Invoice, UsageRecord
from app.main import app


# 1. Setup Mock Models & Services
mock_user_id = uuid.uuid4()
mock_org_id = uuid.uuid4()

mock_user = User(
    id=mock_user_id,
    organization_id=mock_org_id,
    email="test_subscriber@nexora.ai",
    username="test_subscriber",
    first_name="Test",
    last_name="Subscriber",
    is_active=True,
    email_verified=True,
)

mock_organization = Organization(
    id=mock_org_id,
    name="Subscriber Corp",
    slug="subscriber-corp",
    status="active",
    owner_id=mock_user_id,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_plan = Plan(
    id=uuid.uuid4(),
    name="Professional Plan",
    code="professional",
    description="Standard Production Tier",
    price_cents=7900,
    currency="USD",
    billing_interval="monthly",
    features={"max_users": 20, "max_agents": 10, "voice_enabled": True},
)

mock_subscription = Subscription(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    plan_id=mock_plan.id,
    status="active",
    current_period_start=datetime.now(timezone.utc),
    current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    cancel_at_period_end=False,
    plan=mock_plan,
)

mock_invoice = Invoice(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    invoice_number="INV-202607-F1E93",
    subscription_id=mock_subscription.id,
    amount_cents=7900,
    tax_cents=0,
    currency="USD",
    status="paid",
    period_start=datetime.now(timezone.utc),
    period_end=datetime.now(timezone.utc) + timedelta(days=30),
    due_at=datetime.now(timezone.utc),
    paid_at=datetime.now(timezone.utc),
)


class MockPlanRepo:
    async def get_by_code(self, code):
        if code == "professional":
            return mock_plan
        return None

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_plan]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockSubRepo:
    async def get_by_org_id(self, org_id):
        return mock_subscription

    async def create(self, sub):
        sub.id = uuid.uuid4()
        sub.plan = mock_plan
        return sub

    async def update(self, sub):
        return sub

    async def delete(self, sid, org_id):
        return True


class MockInvoiceRepo:
    async def list_by_org_id(self, org_id):
        return [mock_invoice]

    async def create(self, invoice):
        invoice.id = uuid.uuid4()
        return invoice


class MockUsageRepo:
    async def get_usage_by_metric(self, org_id, metric_name):
        return UsageRecord(
            id=uuid.uuid4(),
            organization_id=org_id,
            metric_name=metric_name,
            quantity=5,
            reset_at=datetime.now(timezone.utc) + timedelta(days=30),
        )

    async def create(self, usage):
        return usage

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [
                                    UsageRecord(
                                        id=uuid.uuid4(),
                                        organization_id=mock_org_id,
                                        metric_name="ai_requests",
                                        quantity=5,
                                        reset_at=datetime.now(timezone.utc) + timedelta(days=30),
                                    )
                                ]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockBillingService:
    def __init__(self) -> None:
        self.plan_repo = MockPlanRepo()
        self.sub_repo = MockSubRepo()
        self.invoice_repo = MockInvoiceRepo()
        self.usage_repo = MockUsageRepo()

    async def get_active_subscription(self, org_id) -> Subscription | None:
        return mock_subscription

    async def checkout_subscription(self, organization_id, plan_code, provider, payment_token, coupon_code=None) -> Subscription:
        return mock_subscription

    async def cancel_subscription(self, organization_id) -> Subscription:
        mock_subscription.status = "cancelled"
        mock_subscription.cancel_at_period_end = True
        return mock_subscription


# Setup dependency overrides for billing tests
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_billing_service] = lambda: MockBillingService()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_plans_endpoint(async_client: AsyncClient) -> None:
    """Validate listing plans via GET /api/v1/billing/plans."""
    response = await async_client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["code"] == "professional"


@pytest.mark.asyncio
async def test_get_my_subscription_endpoint(async_client: AsyncClient) -> None:
    """Validate retrieving my subscription via GET /api/v1/billing/subscription/me."""
    response = await async_client.get("/api/v1/billing/subscription/me")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_checkout_subscription_endpoint(async_client: AsyncClient) -> None:
    """Validate checking out subscription via POST /api/v1/billing/subscription/checkout."""
    payload = {
        "plan_code": "professional",
        "provider": "stripe",
        "payment_token": "pm_mock_tok",
    }
    response = await async_client.post("/api/v1/billing/subscription/checkout", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_cancel_subscription_endpoint(async_client: AsyncClient) -> None:
    """Validate cancelling subscription via POST /api/v1/billing/subscription/cancel."""
    response = await async_client.post("/api/v1/billing/subscription/cancel")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_list_invoices_endpoint(async_client: AsyncClient) -> None:
    """Validate listing invoices list via GET /api/v1/billing/invoices."""
    response = await async_client.get("/api/v1/billing/invoices")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["invoice_number"] == "INV-202607-F1E93"


@pytest.mark.asyncio
async def test_get_usage_telemetry_endpoint(async_client: AsyncClient) -> None:
    """Validate usage stats via GET /api/v1/billing/usage."""
    response = await async_client.get("/api/v1/billing/usage")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["metric_name"] == "ai_requests"
