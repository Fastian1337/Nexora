"""
Nexora Platform — Vector Infrastructure & Semantic Search Integration Tests

Validates hybrid RRF retrieval accuracy, HNSW index optimization triggers, and statistics monitors.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

from app.api.deps import get_vector_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.vector import EmbeddingProvider, EmbeddingModel, VectorIndex, SearchHistory
from app.main import app


# 1. Setup Mock Models & Services
mock_user_id = uuid.uuid4()
mock_org_id = uuid.uuid4()
mock_provider_id = uuid.uuid4()
mock_model_id = uuid.uuid4()
mock_kb_id = uuid.uuid4()

mock_user = User(
    id=mock_user_id,
    organization_id=mock_org_id,
    email="test_searcher@nexora.ai",
    username="test_searcher",
    first_name="Test",
    last_name="Searcher",
    is_active=True,
    email_verified=True,
)

mock_organization = Organization(
    id=mock_org_id,
    name="Searcher Corp",
    slug="searcher-corp",
    status="active",
    owner_id=mock_user_id,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_provider = EmbeddingProvider(
    id=mock_provider_id,
    organization_id=mock_org_id,
    name="OpenAI Embeddings",
    code="openai",
    status="active",
)

mock_model = EmbeddingModel(
    id=mock_model_id,
    organization_id=mock_org_id,
    provider_id=mock_provider_id,
    name="OpenAI Small (1536)",
    code="text-embedding-3-small",
    dimensions=1536,
    cost_per_million=2,
    latency_ms=120,
    status="active",
    provider=mock_provider,
)

mock_index = VectorIndex(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    knowledge_base_id=mock_kb_id,
    index_type="hnsw",
    dimensions=1536,
    status="active",
    metrics={"vector_count": 1540, "index_size_bytes": 45000000, "recall_rate": 0.98},
)


class MockProviderRepo:
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


class MockIndexRepo:
    async def get_by_kb(self, kb_id, org_id):
        return mock_index

    async def create(self, idx):
        return idx

    async def update(self, idx):
        return idx

    @property
    def session(self):
        class MockSession:
            async def execute(self, query):
                class MockResult:
                    def scalars(self):
                        class MockScalars:
                            def all(self):
                                return [mock_index]
                        return MockScalars()
                return MockResult()
        return MockSession()


class MockHistoryRepo:
    async def create(self, hist):
        return hist


class MockFeedbackRepo:
    async def create(self, fb):
        return fb


class MockVectorService:
    def __init__(self) -> None:
        self.provider_repo = MockProviderRepo()
        self.model_repo = MockModelRepo()
        self.index_repo = MockIndexRepo()
        self.history_repo = MockHistoryRepo()
        self.feedback_repo = MockFeedbackRepo()

    async def hybrid_search(self, organization_id, knowledge_base_id, query_text, query_vector, top_k=5):
        return [
            {
                "chunk_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "content": "Mock matched text chunk containing clinic onboarding instructions",
                "rrf_score": 0.033,
            }
        ]

    async def rebuild_index(self, organization_id, knowledge_base_id, index_type="hnsw"):
        return mock_index


# Setup dependency overrides for vector tests
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_vector_service] = lambda: MockVectorService()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_embedding_models_endpoint(async_client: AsyncClient) -> None:
    """Validate listing active embedding models via GET /api/v1/vectors/models."""
    response = await async_client.get("/api/v1/vectors/models")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["code"] == "text-embedding-3-small"


@pytest.mark.asyncio
async def test_hybrid_search_endpoint(async_client: AsyncClient) -> None:
    """Validate hybrid search via POST /api/v1/vectors/search."""
    payload = {
        "knowledge_base_id": str(mock_kb_id),
        "query_text": "onboarding manuals",
        "top_k": 5,
    }
    response = await async_client.post("/api/v1/vectors/search", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["hits"]) == 1


@pytest.mark.asyncio
async def test_rebuild_index_endpoint(async_client: AsyncClient) -> None:
    """Validate rebuilding HNSW index via POST /api/v1/vectors/index."""
    payload = {
        "knowledge_base_id": str(mock_kb_id),
        "index_type": "hnsw",
    }
    response = await async_client.post("/api/v1/vectors/index", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_get_statistics_endpoint(async_client: AsyncClient) -> None:
    """Validate statistics monitor logs via GET /api/v1/vectors/statistics."""
    response = await async_client.get("/api/v1/vectors/statistics")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_vectors"] == 1540
