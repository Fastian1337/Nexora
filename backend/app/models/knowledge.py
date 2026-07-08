"""
Nexora Platform — Knowledge Base, Categories, Versions, Chunks, Embeddings & Tag ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func, Integer, Table, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

# Join Table: Collection Documents
collection_documents = Table(
    "collection_documents",
    Base.metadata,
    Column("collection_id", Uuid(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
    Column("document_id", Uuid(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
)

# Join Table: Document Tags
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", Uuid(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class KnowledgeCategory(BaseModel):
    """
    Knowledge Categories table.
    Allows categorization of Knowledge Bases.
    """

    __tablename__ = "knowledge_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    knowledge_bases: Mapped[list[KnowledgeBase]] = relationship("KnowledgeBase", back_populates="category")

    def __repr__(self) -> str:
        return f"<KnowledgeCategory(id={self.id}, name={self.name})>"


class KnowledgeBase(BaseModel):
    """
    Knowledge Bases Table.
    Groups semantic content and document data sources per organization.
    """

    __tablename__ = "knowledge_bases"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    category: Mapped[KnowledgeCategory | None] = relationship("KnowledgeCategory", back_populates="knowledge_bases")
    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
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
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft", index=True)  # Draft, Uploading, Processing, Embedding, Ready, Failed
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase", back_populates="documents")
    versions: Mapped[list[DocumentVersion]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    chunks: Mapped[list[DocumentChunk]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    embedding_jobs: Mapped[list[EmbeddingJob]] = relationship("EmbeddingJob", back_populates="document", cascade="all, delete-orphan")
    embeddings: Mapped[list[Embedding]] = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list[Tag]] = relationship("Tag", secondary=document_tags, back_populates="documents")
    collections: Mapped[list[Collection]] = relationship("Collection", secondary=collection_documents, back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentVersion(BaseModel):
    """
    Tracks upload revisions of individual Document records.
    """

    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    file_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Ready")
    change_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="versions")


class DocumentChunk(BaseModel):
    """
    Split text chunks from documents to feed semantic RAG queries.
    """

    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="chunks")


class EmbeddingJob(BaseModel):
    """
    Asynchronous state tracking mapping document ingestion embedding statuses.
    """

    __tablename__ = "embedding_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)  # pending, running, completed, failed
    error_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="embedding_jobs")


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
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("embedding_models.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content_chunk: Mapped[str] = mapped_column(nullable=False)
    
    # Vector embedding using pgvector (1536-dimensional OpenAI vector defaults)
    vector_embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="embeddings")
    model: Mapped[Any] = relationship("EmbeddingModel", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, doc_id={self.document_id})>"


class Tag(BaseModel):
    """
    General tags metadata nodes.
    """

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Relationships
    documents: Mapped[list[Document]] = relationship("Document", secondary=document_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class Collection(BaseModel):
    """
    Collections grouping multiple documents into logical bundles per organization.
    """

    __tablename__ = "collections"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    documents: Mapped[list[Document]] = relationship("Document", secondary=collection_documents, back_populates="collections")

    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name={self.name})>"
