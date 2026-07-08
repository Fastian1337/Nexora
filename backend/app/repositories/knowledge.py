"""
Nexora Platform — Knowledge Base Data Access Repositories
"""

from __future__ import annotations

import uuid
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.repositories.base import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=KnowledgeBase, session=session)

    async def list_by_org(self, organization_id: uuid.UUID) -> list[KnowledgeBase]:
        query = select(KnowledgeBase).where(
            KnowledgeBase.organization_id == organization_id,
            KnowledgeBase.is_archived == False  # noqa: E712
        ).options(selectinload(KnowledgeBase.category))
        result = await self.session.execute(query)
        return list(result.scalars().all())


class KnowledgeCategoryRepository(BaseRepository[KnowledgeCategory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=KnowledgeCategory, session=session)

    async def get_by_name(self, organization_id: uuid.UUID, name: str) -> KnowledgeCategory | None:
        query = select(KnowledgeCategory).where(
            KnowledgeCategory.organization_id == organization_id,
            KnowledgeCategory.name == name.strip()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Document, session=session)

    async def get_by_id_scoped(self, doc_id: uuid.UUID, organization_id: uuid.UUID) -> Document | None:
        query = select(Document).where(
            Document.id == doc_id,
            Document.organization_id == organization_id
        ).options(
            selectinload(Document.tags),
            selectinload(Document.collections),
            selectinload(Document.chunks)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search_documents(
        self,
        organization_id: uuid.UUID,
        query_string: str | None = None,
        knowledge_base_id: uuid.UUID | None = None,
        status: str | None = None,
        tag_slugs: list[str] | None = None,
    ) -> list[Document]:
        """Perform granular search filters matching titles, status, tags & scopes."""
        conditions = [Document.organization_id == organization_id]

        if knowledge_base_id:
            conditions.append(Document.knowledge_base_id == knowledge_base_id)
        if status:
            conditions.append(Document.status == status)
        if query_string:
            conditions.append(
                or_(
                    Document.title.ilike(f"%{query_string}%"),
                    Document.description.ilike(f"%{query_string}%"),
                    Document.author.ilike(f"%{query_string}%"),
                )
            )

        query = select(Document).where(and_(*conditions)).options(selectinload(Document.tags))

        # Filter by tag slugs if requested
        if tag_slugs:
            query = query.join(Document.tags).where(Tag.slug.in_(tag_slugs))

        result = await self.session.execute(query)
        return list(result.scalars().all())


class DocumentVersionRepository(BaseRepository[DocumentVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=DocumentVersion, session=session)


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=DocumentChunk, session=session)

    async def list_by_document(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class EmbeddingJobRepository(BaseRepository[EmbeddingJob]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=EmbeddingJob, session=session)


class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Tag, session=session)

    async def get_by_slug(self, organization_id: uuid.UUID, slug: str) -> Tag | None:
        query = select(Tag).where(
            Tag.organization_id == organization_id,
            Tag.slug == slug.lower().strip()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class CollectionRepository(BaseRepository[Collection]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Collection, session=session)
