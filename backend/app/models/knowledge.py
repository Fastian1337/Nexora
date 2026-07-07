"""
Nexora Platform — Knowledge Base & Vector Ingestion ORM Models
"""

from __future__ import annotations

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class KnowledgeBase(BaseModel):
    """
    Knowledge Bases Table.
    Groups semantic content and document data sources per organization.
    """

    __tablename__ = "knowledge_bases"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    # Relationships
    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    agents: Mapped[list[AiAgent]] = relationship(
        "AiAgent",
        back_populates="knowledge_base",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeBase(id={self.id}, name={self.name}, org={self.organization_id})>"


class Document(BaseModel):
    """
    Documents Table.
    Represents raw sources ingested into a Knowledge Base.
    """

    __tablename__ = "documents"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("files.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing", index=True)

    # Relationships
    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase", back_populates="documents")
    embeddings: Mapped[list[Embedding]] = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title})>"


class Embedding(BaseModel):
    """
    Embeddings Table.
    Contains granular text chunks and their corresponding high-dimensional vector representations.
    """

    __tablename__ = "embeddings"

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_chunk: Mapped[str] = mapped_column(nullable=False)
    
    # Vector embedding using pgvector (1536-dimensional OpenAI vector defaults)
    vector_embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, doc_id={self.document_id})>"
