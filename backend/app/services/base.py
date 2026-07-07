"""
Nexora Platform — Base Service

Base service class that all application services inherit from.
Services orchestrate business logic by coordinating between
repositories and other services.

Usage:
    class UserService(BaseService[UserRepository]):
        def __init__(self, repository: UserRepository):
            super().__init__(repository)

        async def get_user_profile(self, user_id: UUID, org_id: UUID):
            user = await self.repository.get_by_id(user_id, org_id)
            if not user:
                raise NotFoundException("User not found")
            return user
"""

from __future__ import annotations

from typing import Generic, TypeVar

from app.config.logging import get_logger
from app.repositories.base import BaseRepository

RepoT = TypeVar("RepoT", bound=BaseRepository)  # type: ignore[type-arg]

logger = get_logger(__name__)


class BaseService(Generic[RepoT]):
    """
    Abstract base service with repository injection.

    Services encapsulate business logic and use cases.
    They depend on repositories for data access, never on
    the database session directly.

    Type Parameters:
        RepoT: The repository type this service uses.

    Attributes:
        repository: The injected repository instance.
    """

    def __init__(self, repository: RepoT) -> None:
        """
        Initialize the service with a repository.

        Args:
            repository: The repository instance for data access.
        """
        self.repository = repository
        self._logger = get_logger(self.__class__.__name__)
