"""
Nexora Platform — Vector Infrastructure Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.base import BaseSchema


class EmbeddingModelResponse(BaseSchema):
    id: uuid.UUID
    name: str
    code: str
    dimensions: int
    cost_per_million: int
    latency_ms: int
    status: str


class VectorSearchRequest(BaseSchema):
    knowledge_base_id: uuid.UUID
    query_text: str = Field(min_length=1, max_length=1000)
    query_vector: list[float] = Field(default_factory=list)  # Optional input vector matching dimensions
    top_k: int = Field(default=5, ge=1, le=100)


class VectorSearchHit(BaseSchema):
    chunk_id: str
    document_id: str
    content: str
    rrf_score: float


class VectorSearchResponse(BaseSchema):
    hits: list[VectorSearchHit]
    latency_ms: int
    recall_rate: float = 0.98


class VectorIndexRebuildRequest(BaseSchema):
    knowledge_base_id: uuid.UUID
    index_type: str = Field(default="hnsw", pattern=r"^(hnsw|ivfflat|exact)$")


class VectorIndexResponse(BaseSchema):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    index_type: str
    dimensions: int
    status: str
    metrics: dict[str, Any]
    created_at: datetime
