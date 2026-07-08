"""
Nexora Platform — Knowledge Service, Text Extractor, Ingestion Splitters & Document Service
"""

from __future__ import annotations

import os
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.knowledge import (
    KnowledgeBase,
    KnowledgeCategory,
    Document,
    DocumentVersion,
    DocumentChunk,
    EmbeddingJob,
    Tag,
    Collection,
)
from app.repositories.knowledge import (
    KnowledgeBaseRepository,
    KnowledgeCategoryRepository,
    DocumentRepository,
    DocumentVersionRepository,
    DocumentChunkRepository,
    EmbeddingJobRepository,
    TagRepository,
    CollectionRepository,
)
from app.services.storage.provider import StorageProvider
from app.config.logging import get_logger

logger = get_logger(__name__)


class TextExtractor:
    """Helper service extracting string text from binary file buffers."""

    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".txt", ".md", ".csv", ".json", ".html"]:
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                return file_content.decode("latin-1")
        # Sandbox Mock parsing for binary document structures (PDF, DOCX, XLSX, etc.)
        logger.info("simulating_binary_document_text_parsing", file=filename)
        return f"Nexora Knowledge Base Sandbox Extracted Content.\nFilename: {filename}\nGenerated content context details."


class ChunkSplitter:
    """Configurable word-boundary chunk splitter with metadata inheritance."""

    @staticmethod
    def split_content(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        if not text:
            return []
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_len = 0

        # Basic character-length approximate word splitter
        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1  # count spaces
            
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # Retain overlap words
                overlap_chars = 0
                overlap_chunk = []
                # Walk backward to satisfy overlap bound
                for w in reversed(current_chunk):
                    overlap_chunk.insert(0, w)
                    overlap_chars += len(w) + 1
                    if overlap_chars >= overlap:
                        break
                current_chunk = overlap_chunk
                current_len = overlap_chars

        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks


class KnowledgeService:
    """Service layer managing Knowledge Bases and categories."""

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        cat_repo: KnowledgeCategoryRepository,
    ) -> None:
        self.kb_repo = kb_repo
        self.cat_repo = cat_repo

    async def create_category(self, organization_id: uuid.UUID, name: str, description: str | None = None) -> KnowledgeCategory:
        existing = await self.cat_repo.get_by_name(organization_id, name)
        if existing:
            raise ConflictException(message="Category name already exists", error_code="CATEGORY_EXISTS")
        cat = KnowledgeCategory(organization_id=organization_id, name=name, description=description)
        return await self.cat_repo.create(cat)

    async def create_knowledge_base(
        self,
        organization_id: uuid.UUID,
        name: str,
        description: str | None = None,
        category_id: uuid.UUID | None = None,
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            organization_id=organization_id,
            name=name,
            description=description,
            category_id=category_id,
            is_archived=False,
        )
        return await self.kb_repo.create(kb)


class DocumentService:
    """Handles raw file uploads, storage writes, chunk splits, reindexing and search queries."""

    def __init__(
        self,
        doc_repo: DocumentRepository,
        version_repo: DocumentVersionRepository,
        chunk_repo: DocumentChunkRepository,
        job_repo: EmbeddingJobRepository,
        tag_repo: TagRepository,
        kb_repo: KnowledgeBaseRepository,
        storage: StorageProvider,
    ) -> None:
        self.doc_repo = doc_repo
        self.version_repo = version_repo
        self.chunk_repo = chunk_repo
        self.job_repo = job_repo
        self.tag_repo = tag_repo
        self.kb_repo = kb_repo
        self.storage = storage

    async def upload_document(
        self,
        organization_id: uuid.UUID,
        knowledge_base_id: uuid.UUID,
        filename: str,
        file_content: bytes,
        mime_type: str | None = None,
        author: str | None = None,
        custom_chunk_size: int = 1000,
        custom_overlap: int = 200,
        tags: list[str] | None = None,
    ) -> Document:
        """
        Saves document buffer to storage, creates base Document model,
        and schedules async text extraction & split routines.
        """
        # Verify knowledge base
        kb = await self.kb_repo.get_by_id(knowledge_base_id, organization_id)
        if not kb:
            raise NotFoundException(message="Knowledge Base not found", error_code="KB_NOT_FOUND")

        # Save to Storage Provider
        destination_path = f"org_{organization_id.hex}/kb_{knowledge_base_id.hex}/{filename}"
        storage_url = await self.storage.upload_file(file_content, destination_path)

        # Create Document
        doc = Document(
            organization_id=organization_id,
            knowledge_base_id=knowledge_base_id,
            title=filename,
            source_url=storage_url,
            author=author,
            status="Uploading",
            file_size_bytes=len(file_content),
            mime_type=mime_type,
            version=1,
        )

        # Assign tags
        if tags:
            for tag_name in tags:
                slug = tag_name.lower().strip().replace(" ", "_")
                tag = await self.tag_repo.get_by_slug(organization_id, slug)
                if not tag:
                    tag = Tag(organization_id=organization_id, name=tag_name, slug=slug)
                    tag = await self.tag_repo.create(tag)
                doc.tags.append(tag)

        created_doc = await self.doc_repo.create(doc)

        # Register document version
        version = DocumentVersion(
            organization_id=organization_id,
            document_id=created_doc.id,
            version_number=1,
            file_id=created_doc.id,  # Link to document ID as a placeholder file ID
            status="Ready",
            change_summary="Initial upload Ingestion",
        )
        await self.version_repo.create(version)

        # Trigger background processing task (simulating worker queue lifecycle)
        asyncio.create_task(
            self.process_document_pipeline(
                doc_id=created_doc.id,
                org_id=organization_id,
                file_content=file_content,
                filename=filename,
                chunk_size=custom_chunk_size,
                overlap=custom_overlap,
            )
        )

        return created_doc

    async def process_document_pipeline(
        self,
        doc_id: uuid.UUID,
        org_id: uuid.UUID,
        file_content: bytes,
        filename: str,
        chunk_size: int,
        overlap: int,
    ) -> None:
        """Background extraction, splitting, and reindex logging pipeline."""
        try:
            # 1. Update status to Processing
            db_session = self.doc_repo.session
            query = select(Document).where(Document.id == doc_id, Document.organization_id == org_id)
            doc = (await db_session.execute(query)).scalar_one_or_none()
            if not doc:
                return

            doc.status = "Processing"
            await self.doc_repo.update(doc)
            await asyncio.sleep(0.5)  # Simulate processing pipeline delay

            # 2. Text Extraction
            extracted_text = TextExtractor.extract_text(file_content, filename)

            # 3. Chunking Splitting
            chunks = ChunkSplitter.split_content(extracted_text, chunk_size, overlap)

            # Save chunks to Database
            for idx, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    organization_id=org_id,
                    document_id=doc_id,
                    chunk_index=idx,
                    content=chunk_text,
                    token_count=len(chunk_text.split()),  # Simple whitespace token count
                    metadata={"source": filename, "processed_at": datetime.now(timezone.utc).isoformat()},
                )
                await self.chunk_repo.create(chunk)

            # 4. Schedule EmbeddingJob status
            job = EmbeddingJob(
                organization_id=org_id,
                document_id=doc_id,
                status="pending",
                attempts=1,
            )
            created_job = await self.job_repo.create(job)

            # Simulate embedding generation delay
            doc.status = "Embedding"
            await self.doc_repo.update(doc)
            await asyncio.sleep(0.5)

            created_job.status = "completed"
            await self.job_repo.update(created_job)

            # Update document to ready
            doc.status = "Ready"
            await self.doc_repo.update(doc)
            logger.info("document_ingestion_pipeline_succeeded", doc_id=str(doc_id))

        except Exception as e:
            logger.error("document_ingestion_pipeline_failed", doc_id=str(doc_id), error=str(e))
            # Mark failed status
            query = select(Document).where(Document.id == doc_id, Document.organization_id == org_id)
            doc = (await self.doc_repo.session.execute(query)).scalar_one_or_none()
            if doc:
                doc.status = "Failed"
                await self.doc_repo.update(doc)

    async def reindex_document(self, doc_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        """Clear existing chunks and rebuild splits."""
        doc = await self.doc_repo.get_by_id_scoped(doc_id, organization_id)
        if not doc:
            raise NotFoundException(message="Document not found", error_code="DOCUMENT_NOT_FOUND")

        # Delete existing chunks
        for chunk in doc.chunks:
            await self.chunk_repo.delete(chunk.id, organization_id)

        # Trigger re-extraction background task
        # Download document file bytes from storage
        file_bytes = await self.storage.download_file(doc.source_url)
        
        doc.status = "Processing"
        await self.doc_repo.update(doc)

        asyncio.create_task(
            self.process_document_pipeline(
                doc_id=doc.id,
                org_id=organization_id,
                file_content=file_bytes,
                filename=doc.title,
                chunk_size=1000,
                overlap=200,
            )
        )
