"""
Nexora Platform — Vector Infrastructure & Semantic Search ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class EmbeddingProvider(BaseModel):
    """
    Embedding Providers registry (OpenAI, Gemini, Local models, etc.).
    """

    __tablename__ = "embedding_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # openai, gemini, local
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    # Relationships
    models: Mapped[list[EmbeddingModel]] = relationship("EmbeddingModel", back_populates="provider", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<EmbeddingProvider(id={self.id}, code={self.code})>"


class EmbeddingModel(BaseModel):
    """
    Seeded dimension settings and latency telemetry for vectorizers models.
    """

    __tablename__ = "embedding_models"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("embedding_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)  # text-embedding-3-small, etc.
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=1536)
    cost_per_million: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # in cents
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    # Relationships
    provider: Mapped[EmbeddingProvider] = relationship("EmbeddingProvider", back_populates="models")
    embeddings: Mapped[list[Embedding]] = relationship("Embedding", back_populates="model")

    def __repr__(self) -> str:
        return f"<EmbeddingModel(id={self.id}, code={self.code})>"


class VectorIndex(BaseModel):
    """
    Vector indexes (HNSW or IVFFlat) built per organization Knowledge Base.
    """

    __tablename__ = "vector_indexes"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index_type: Mapped[str] = mapped_column(String(50), nullable=False, default="hnsw")  # hnsw, ivfflat, exact
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=1536)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)  # building, active, degraded
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)  # index_size_bytes, recall_rate, vector_count

    def __repr__(self) -> str:
        return f"<VectorIndex(id={self.id}, kb_id={self.knowledge_base_id}, type={self.index_type})>"


class SearchHistory(BaseModel):
    """
    Semantic search request query tracker logging performance recall rates.
    """

    __tablename__ = "vector_search_histories"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    results_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    feedbacks: Mapped[list[SearchFeedback]] = relationship("SearchFeedback", back_populates="search_history", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, results={self.results_count}, latency={self.latency_ms}ms)>"


class SearchFeedback(BaseModel):
    """
    Client user feedback rating retrieval relevance.
    """

    __tablename__ = "vector_search_feedbacks"

    search_history_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("vector_search_histories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5 rating scale
    comments: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    search_history: Mapped[SearchHistory] = relationship("SearchHistory", back_populates="feedbacks")
