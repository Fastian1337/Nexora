"""
Nexora Platform — AI Gateway Ingestion Integration Tests

Validates registered model registry endpoints, chat completions prompt variables execution,
streaming SSE chunk logs, and provider health monitors.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

from app.api.deps import get_ai_gateway, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.ai_gateway import AIProvider, AIModel, AIRequest, ProviderHealth
from app.main import app


# 1. Setup Mock Models & Services
mock_user_id = uuid.uuid4()
mock_org_id = uuid.uuid4()
mock_provider_id = uuid.uuid4()
mock_model_id = uuid.uuid4()

mock_user = User(
    id=mock_user_id,
    organization_id=mock_org_id,
    email="test_developer@nexora.ai",
    username="test_developer",
    first_name="Test",
    last_name="Developer",
    is_active=True,
    email_verified=True,
)

mock_organization = Organization(
    id=mock_org_id,
    name="Developer Corp",
    slug="developer-corp",
    status="active",
    owner_id=mock_user_id,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_provider = AIProvider(
    id=mock_provider_id,
    organization_id=mock_org_id,
    name="OpenAI Sandbox",
    code="openai",
    base_url="https://api.openai.com/v1",
    status="active",
)

mock_model = AIModel(
    id=mock_model_id,
    organization_id=mock_org_id,
    provider_id=mock_provider_id,
    name="GPT-4o Sandbox",
    code="gpt-4o",
    capabilities={"vision": True, "tools": True},
    context_window=128000,
    cost_prompt_per_million=3000,
    cost_completion_per_million=15000,
    status="active",
    provider=mock_provider,
)

mock_request = AIRequest(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    model_id=mock_model_id,
    user_id=mock_user_id,
    prompt_tokens=45,
    completion_tokens=25,
    total_tokens=70,
    estimated_cost_cents=12,
    latency_ms=450,
    status="succeeded",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_health = ProviderHealth(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    provider_id=mock_provider_id,
    status="healthy",
    error_rate=0.0,
    latency_ms=320,
    last_checked_at=datetime.now(timezone.utc),
)


class MockProviderRepo:
    async def list_active(self, organization_id):
        return [mock_provider]

    async def get_by_code(self, org_id, code):
        return mock_provider


class MockModelRepo:
    async def get_by_code(self, org_id, code):
        return mock_model

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_model]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockRequestRepo:
    async def create(self, req):
        req.id = uuid.uuid4()
        return req

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_request]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockResponseRepo:
    async def create(self, resp):
        return resp


class MockHealthRepo:
    async def get_latest_health(self, provider_id):
        return mock_health

    async def create(self, health):
        return health

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_health]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockAiGateway:
    def __init__(self) -> None:
        self.provider_repo = MockProviderRepo()
        self.model_repo = MockModelRepo()
        self.request_repo = MockRequestRepo()
        self.response_repo = MockResponseRepo()
        self.health_repo = MockHealthRepo()

    async def chat(self, organization_id, user_id, model_code, messages, temperature=0.7, max_tokens=1000, json_output=False) -> dict:
        return {
            "response_text": "Mock completion response",
            "total_tokens": 70,
            "cost_cents": 12,
            "model": "gpt-4o",
        }

    async def stream_chat(self, organization_id, user_id, model_code, messages, temperature=0.7, max_tokens=1000, json_output=False):
        async def generator():
            yield {"chunk_text": "Mock chunk", "finish_reason": None}
            yield {"chunk_text": " response", "finish_reason": "stop"}
        return generator()


# Setup dependency overrides for AI tests
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_ai_gateway] = lambda: MockAiGateway()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_providers_endpoint(async_client: AsyncClient) -> None:
    """Validate listing providers via GET /api/v1/ai/providers."""
    response = await async_client.get("/api/v1/ai/providers")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["code"] == "openai"


@pytest.mark.asyncio
async def test_list_models_endpoint(async_client: AsyncClient) -> None:
    """Validate listing models registry via GET /api/v1/ai/models."""
    response = await async_client.get("/api/v1/ai/models")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["code"] == "gpt-4o"


@pytest.mark.asyncio
async def test_chat_completions_endpoint(async_client: AsyncClient) -> None:
    """Validate standard chat via POST /api/v1/ai/chat."""
    payload = {
        "model_code": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello!"},
        ],
    }
    response = await async_client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["response_text"] == "Mock completion response"


@pytest.mark.asyncio
async def test_streaming_completions_endpoint(async_client: AsyncClient) -> None:
    """Validate SSE stream chat via POST /api/v1/ai/stream."""
    payload = {
        "model_code": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello!"}],
    }
    response = await async_client.post("/api/v1/ai/stream", json=payload)
    assert response.status_code == 200
    # Streaming responses are chunks
    body = response.text
    assert "data: " in body


@pytest.mark.asyncio
async def test_usage_telemetry_endpoint(async_client: AsyncClient) -> None:
    """Validate token costs ledger lists via GET /api/v1/ai/usage."""
    response = await async_client.get("/api/v1/ai/usage")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["total_tokens"] == 70


@pytest.mark.asyncio
async def test_health_checkpoints_endpoint(async_client: AsyncClient) -> None:
    """Validate health monitors via GET /api/v1/ai/health."""
    response = await async_client.get("/api/v1/ai/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["status"] == "healthy"
