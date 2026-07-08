"""
Nexora Platform — AI Gateway & Central Model Registry ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AIProvider(BaseModel):
    """
    AI Providers registry (OpenAI, Gemini, Anthropic, Ollama, etc.).
    Holds credential hashes and routing statuses.
    """

    __tablename__ = "ai_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)  # active, inactive
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    models: Mapped[list[AIModel]] = relationship("AIModel", back_populates="provider", cascade="all, delete-orphan")
    health_checks: Mapped[list[ProviderHealth]] = relationship("ProviderHealth", back_populates="provider", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AIProvider(id={self.id}, code={self.code})>"


class AIModel(BaseModel):
    """
    Central AI Model Registry defining context, capabilities, and unit costs.
    """

    __tablename__ = "ai_models"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)  # gpt-4o, claude-3-5-sonnet
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="latest")
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)  # vision, tools, stream, reasoning
    context_window: Mapped[int] = mapped_column(Integer, nullable=False, default=4096)
    cost_prompt_per_million: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # in cents
    cost_completion_per_million: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # in cents
    latency_ms_avg: Mapped[int] = mapped_column(Integer, nullable=False, default=1500)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    # Relationships
    provider: Mapped[AIProvider] = relationship("AIProvider", back_populates="models")
    requests: Mapped[list[AIRequest]] = relationship("AIRequest", back_populates="model")


class PromptTemplate(BaseModel):
    """
    Central Developer and User Prompt Template registers.
    """

    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    versions: Mapped[list[PromptVersion]] = relationship("PromptVersion", back_populates="template", cascade="all, delete-orphan")


class PromptVersion(BaseModel):
    """
    Variables templates and system instructions version logs.
    """

    __tablename__ = "prompt_versions"

    template_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("prompt_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    system_prompt: Mapped[str] = mapped_column(nullable=False)
    developer_prompt: Mapped[str | None] = mapped_column(nullable=True)
    user_prompt_template: Mapped[str] = mapped_column(nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)  # list of template parameter strings
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    template: Mapped[PromptTemplate] = relationship("PromptTemplate", back_populates="versions")


class AIRequest(BaseModel):
    """
    Telemetry log details mapping prompts cost parameters and tokens counts.
    """

    __tablename__ = "ai_requests"

    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="succeeded", index=True)

    # Relationships
    model: Mapped[AIModel] = relationship("AIModel", back_populates="requests")
    response: Mapped[AIResponse | None] = relationship("AIResponse", back_populates="request", cascade="all, delete-orphan", uselist=False)


class AIResponse(BaseModel):
    """
    Completed logs holding parsed completions and reasons.
    """

    __tablename__ = "ai_responses"

    request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    response_text: Mapped[str] = mapped_column(nullable=False)
    finish_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    request: Mapped[AIRequest] = relationship("AIRequest", back_populates="response")


class ProviderHealth(BaseModel):
    """
    Heartbeat and errors rate tracking checklists.
    """

    __tablename__ = "provider_health"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")  # healthy, degraded, offline
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    provider: Mapped[AIProvider] = relationship("AIProvider", back_populates="health_checks")
