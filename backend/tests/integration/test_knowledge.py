"""
Nexora Platform — Knowledge Base Ingestion Integration Tests

Validates Knowledge Base container registrations, file uploads, mock text parses,
reindexing triggers, search query filters, and storage cleanup tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

from app.api.deps import get_knowledge_service, get_document_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.knowledge import KnowledgeBase, Document, DocumentChunk
from app.main import app


# 1. Setup Mock Models & Services
mock_user_id = uuid.uuid4()
mock_org_id = uuid.uuid4()
mock_kb_id = uuid.uuid4()

mock_user = User(
    id=mock_user_id,
    organization_id=mock_org_id,
    email="test_curator@nexora.ai",
    username="test_curator",
    first_name="Test",
    last_name="Curator",
    is_active=True,
    email_verified=True,
)

mock_organization = Organization(
    id=mock_org_id,
    name="Curator Corp",
    slug="curator-corp",
    status="active",
    owner_id=mock_user_id,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_kb = KnowledgeBase(
    id=mock_kb_id,
    organization_id=mock_org_id,
    name="Clinic Policies",
    description="Knowledge base for internal healthcare staff policies",
    is_archived=False,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)

mock_document = Document(
    id=uuid.uuid4(),
    organization_id=mock_org_id,
    knowledge_base_id=mock_kb_id,
    title="admissions_manual.txt",
    source_url="/storage/mock_admissions.txt",
    author="Admin Staff",
    status="Ready",
    file_size_bytes=1024,
    mime_type="text/plain",
    version=1,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)


class MockKBRepo:
    async def get_by_id(self, kb_id, org_id):
        if kb_id == mock_kb_id:
            return mock_kb
        return None

    async def list_by_org(self, organization_id):
        return [mock_kb]

    async def create(self, kb):
        kb.id = uuid.uuid4()
        return kb

    async def update(self, kb):
        return kb


class MockDocRepo:
    async def get_by_id_scoped(self, doc_id, org_id):
        return mock_document

    async def search_documents(self, organization_id, query_string=None, knowledge_base_id=None, status=None):
        return [mock_document]

    async def create(self, doc):
        doc.id = uuid.uuid4()
        return doc

    async def delete(self, doc_id, org_id):
        return True


class MockStorage:
    async def upload_file(self, content, destination):
        return f"/storage/{destination}"

    async def download_file(self, url):
        return b"Mock parsed text content from file."

    async def delete_file(self, url):
        return True


class MockKBService:
    def __init__(self) -> None:
        self.kb_repo = MockKBRepo()

    async def create_knowledge_base(self, organization_id, name, description=None, category_id=None):
        return mock_kb


class MockDocService:
    def __init__(self) -> None:
        self.doc_repo = MockDocRepo()
        self.storage = MockStorage()

    async def upload_document(self, organization_id, knowledge_base_id, filename, file_content, mime_type=None, author=None, custom_chunk_size=1000, custom_overlap=200):
        return mock_document

    async def reindex_document(self, doc_id, org_id):
        pass


# Setup dependency overrides for knowledge tests
@pytest.fixture(autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_knowledge_service] = lambda: MockKBService()
    app.dependency_overrides[get_document_service] = lambda: MockDocService()
    app.dependency_overrides[get_current_organization] = lambda: mock_organization
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_knowledge_bases_endpoint(async_client: AsyncClient) -> None:
    """Validate listing bases via GET /api/v1/knowledge."""
    response = await async_client.get("/api/v1/knowledge")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["name"] == "Clinic Policies"


@pytest.mark.asyncio
async def test_create_knowledge_base_endpoint(async_client: AsyncClient) -> None:
    """Validate creating bases via POST /api/v1/knowledge."""
    payload = {"name": "School Policies", "description": "Admission guidelines."}
    response = await async_client.post("/api/v1/knowledge", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_upload_document_endpoint(async_client: AsyncClient) -> None:
    """Validate uploading document via POST /api/v1/knowledge/documents/upload."""
    files = {"file": ("admissions_manual.txt", b"Mock raw content", "text/plain")}
    data = {
        "knowledge_base_id": str(mock_kb_id),
        "author": "Staff",
        "chunk_size": "1000",
        "overlap": "200",
    }
    response = await async_client.post("/api/v1/knowledge/documents/upload", files=files, data=data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["title"] == "admissions_manual.txt"


@pytest.mark.asyncio
async def test_list_documents_endpoint(async_client: AsyncClient) -> None:
    """Validate listing documents via GET /api/v1/knowledge/documents."""
    response = await async_client.get("/api/v1/knowledge/documents")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1


@pytest.mark.asyncio
async def test_get_document_details_endpoint(async_client: AsyncClient) -> None:
    """Validate getting details via GET /api/v1/knowledge/documents/{id}."""
    doc_uuid = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/knowledge/documents/{doc_uuid}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_reindex_document_endpoint(async_client: AsyncClient) -> None:
    """Validate reindexing splits via POST /api/v1/knowledge/documents/{id}/reindex."""
    doc_uuid = str(uuid.uuid4())
    response = await async_client.post(f"/api/v1/knowledge/documents/{doc_uuid}/reindex")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True


@pytest.mark.asyncio
async def test_delete_document_endpoint(async_client: AsyncClient) -> None:
    """Validate purging document via DELETE /api/v1/knowledge/documents/{id}."""
    doc_uuid = str(uuid.uuid4())
    response = await async_client.delete(f"/api/v1/knowledge/documents/{doc_uuid}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
