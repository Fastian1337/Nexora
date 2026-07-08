"""
Nexora Platform — Vector Infrastructure Data Access Repositories
"""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vector import (
    EmbeddingProvider,
    EmbeddingModel,
    VectorIndex,
    SearchHistory,
    SearchFeedback,
)
from app.repositories.base import BaseRepository


class EmbeddingProviderRepository(BaseRepository[EmbeddingProvider]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=EmbeddingProvider, session=session)

    async def get_by_code(self, organization_id: uuid.UUID, code: str) -> EmbeddingProvider | None:
        query = select(EmbeddingProvider).where(
            EmbeddingProvider.organization_id == organization_id,
            EmbeddingProvider.code == code.lower().strip()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_active(self, organization_id: uuid.UUID) -> list[EmbeddingProvider]:
        query = select(EmbeddingProvider).where(
            EmbeddingProvider.organization_id == organization_id,
            EmbeddingProvider.status == "active"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class EmbeddingModelRepository(BaseRepository[EmbeddingModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=EmbeddingModel, session=session)

    async def get_by_code(self, organization_id: uuid.UUID, code: str) -> EmbeddingModel | None:
        query = select(EmbeddingModel).where(
            EmbeddingModel.organization_id == organization_id,
            EmbeddingModel.code == code.lower().strip()
        ).options(selectinload(EmbeddingModel.provider))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_provider(self, provider_id: uuid.UUID) -> list[EmbeddingModel]:
        query = select(EmbeddingModel).where(
            EmbeddingModel.provider_id == provider_id,
            EmbeddingModel.status == "active"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class VectorIndexRepository(BaseRepository[VectorIndex]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=VectorIndex, session=session)

    async def get_by_kb(self, knowledge_base_id: uuid.UUID, organization_id: uuid.UUID) -> VectorIndex | None:
        query = select(VectorIndex).where(
            VectorIndex.knowledge_base_id == knowledge_base_id,
            VectorIndex.organization_id == organization_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class SearchHistoryRepository(BaseRepository[SearchHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=SearchHistory, session=session)

    async def list_by_org(self, organization_id: uuid.UUID) -> list[SearchHistory]:
        query = select(SearchHistory).where(
            SearchHistory.organization_id == organization_id
        ).order_by(SearchHistory.created_at.desc()).options(selectinload(SearchHistory.feedbacks))
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SearchFeedbackRepository(BaseRepository[SearchFeedback]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=SearchFeedback, session=session)
