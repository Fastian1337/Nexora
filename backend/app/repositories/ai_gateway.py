"""
Nexora Platform — AI Gateway Data Access Repositories
"""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_gateway import (
    AIProvider,
    AIModel,
    PromptTemplate,
    PromptVersion,
    AIRequest,
    AIResponse,
    ProviderHealth,
)
from app.repositories.base import BaseRepository


class AIProviderRepository(BaseRepository[AIProvider]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AIProvider, session=session)

    async def get_by_code(self, organization_id: uuid.UUID, code: str) -> AIProvider | None:
        query = select(AIProvider).where(
            AIProvider.organization_id == organization_id,
            AIProvider.code == code.lower().strip()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_active(self, organization_id: uuid.UUID) -> list[AIProvider]:
        query = select(AIProvider).where(
            AIProvider.organization_id == organization_id,
            AIProvider.status == "active"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class AIModelRepository(BaseRepository[AIModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AIModel, session=session)

    async def get_by_code(self, organization_id: uuid.UUID, code: str) -> AIModel | None:
        query = select(AIModel).where(
            AIModel.organization_id == organization_id,
            AIModel.code == code.lower().strip()
        ).options(selectinload(AIModel.provider))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_provider(self, provider_id: uuid.UUID) -> list[AIModel]:
        query = select(AIModel).where(
            AIModel.provider_id == provider_id,
            AIModel.status == "active"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class PromptTemplateRepository(BaseRepository[PromptTemplate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=PromptTemplate, session=session)

    async def get_by_code(self, organization_id: uuid.UUID, code: str) -> PromptTemplate | None:
        query = select(PromptTemplate).where(
            PromptTemplate.organization_id == organization_id,
            PromptTemplate.code == code.lower().strip()
        ).options(selectinload(PromptTemplate.versions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class PromptVersionRepository(BaseRepository[PromptVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=PromptVersion, session=session)


class AIRequestRepository(BaseRepository[AIRequest]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AIRequest, session=session)

    async def get_with_response(self, request_id: uuid.UUID, organization_id: uuid.UUID) -> AIRequest | None:
        query = select(AIRequest).where(
            AIRequest.id == request_id,
            AIRequest.organization_id == organization_id
        ).options(
            selectinload(AIRequest.model),
            selectinload(AIRequest.response)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class AIResponseRepository(BaseRepository[AIResponse]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AIResponse, session=session)


class ProviderHealthRepository(BaseRepository[ProviderHealth]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=ProviderHealth, session=session)

    async def get_latest_health(self, provider_id: uuid.UUID) -> ProviderHealth | None:
        query = select(ProviderHealth).where(
            ProviderHealth.provider_id == provider_id
        ).order_by(ProviderHealth.last_checked_at.desc())
        result = await self.session.execute(query)
        return result.scalars().first()
