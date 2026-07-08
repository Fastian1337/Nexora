"""
Nexora Platform — AI Gateway Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.base import BaseSchema


class AIProviderResponse(BaseSchema):
    id: uuid.UUID
    name: str
    code: str
    base_url: str | None
    status: str


class AIModelResponse(BaseSchema):
    id: uuid.UUID
    name: str
    code: str
    version: str
    capabilities: dict[str, Any]
    context_window: int
    cost_prompt_per_million: int
    cost_completion_per_million: int
    latency_ms_avg: int
    status: str


class ChatMessage(BaseSchema):
    role: str = Field(pattern=r"^(system|user|assistant|developer)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseSchema):
    model_code: str = Field(default="gpt-4o")
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    json_output: bool = Field(default=False)


class ChatResponse(BaseSchema):
    response_text: str
    total_tokens: int
    cost_cents: int
    model: str


class HealthCheckResponse(BaseSchema):
    id: uuid.UUID
    provider_id: uuid.UUID
    status: str
    error_rate: float
    latency_ms: int
    last_checked_at: datetime


class TokenUsageResponse(BaseSchema):
    id: uuid.UUID
    model_id: uuid.UUID
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_cents: int
    latency_ms: int
    created_at: datetime
