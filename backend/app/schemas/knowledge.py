"""
Nexora Platform — Knowledge Base Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.base import BaseSchema


class KnowledgeCategoryResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None


class KnowledgeBaseCreate(BaseSchema):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    category_id: uuid.UUID | None = Field(default=None)


class KnowledgeBaseUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    category_id: uuid.UUID | None = Field(default=None)


class TagResponse(BaseSchema):
    id: uuid.UUID
    name: str
    slug: str


class CollectionResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None


class KnowledgeBaseResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    category_id: uuid.UUID | None
    is_archived: bool
    category: KnowledgeCategoryResponse | None = None
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseSchema):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    file_id: uuid.UUID | None
    title: str
    description: str | None
    source_url: str | None
    author: str | None
    language: str
    status: str
    file_size_bytes: int
    mime_type: str | None
    version: int
    tags: list[TagResponse] = []
    collections: list[CollectionResponse] = []
    created_at: datetime


class DocumentChunkResponse(BaseSchema):
    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int
    metadata: dict[str, Any]
