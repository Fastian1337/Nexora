"""
Nexora Platform — Central AI Gateway Orchestrator Service
"""

from __future__ import annotations

import json
import uuid
import time
from typing import Any, AsyncGenerator
from sqlalchemy import select

from app.core.exceptions import NotFoundException, ValidationException
from app.models.ai_gateway import (
    AIProvider,
    AIModel,
    PromptTemplate,
    PromptVersion,
    AIRequest,
    AIResponse,
    ProviderHealth,
)
from app.repositories.ai_gateway import (
    AIProviderRepository,
    AIModelRepository,
    PromptTemplateRepository,
    PromptVersionRepository,
    AIRequestRepository,
    AIResponseRepository,
    ProviderHealthRepository,
)
from app.services.ai.providers import OpenAiProvider, GeminiProvider, AnthropicProvider, OllamaProvider
from app.config.logging import get_logger

logger = get_logger(__name__)


class PromptRenderer:
    """Utility class rendering template strings with keyword mappings."""

    @staticmethod
    def render(template_str: str, variables: dict[str, Any]) -> str:
        rendered = template_str
        for key, val in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(val))
        return rendered


class AiGateway:
    """
    Central AI Gateway service implementing prompt variables rendering,
    intelligent provider routing, and token usage cost tracking logs.
    """

    def __init__(
        self,
        provider_repo: AIProviderRepository,
        model_repo: AIModelRepository,
        template_repo: PromptTemplateRepository,
        version_repo: PromptVersionRepository,
        request_repo: AIRequestRepository,
        response_repo: AIResponseRepository,
        health_repo: ProviderHealthRepository,
    ) -> None:
        self.provider_repo = provider_repo
        self.model_repo = model_repo
        self.template_repo = template_repo
        self.version_repo = version_repo
        self.request_repo = request_repo
        self.response_repo = response_repo
        self.health_repo = health_repo

    def _resolve_provider_client(self, code: str) -> Any:
        code_lower = code.lower().strip()
        if code_lower == "openai":
            return OpenAiProvider()
        elif code_lower == "gemini":
            return GeminiProvider()
        elif code_lower == "anthropic":
            return AnthropicProvider()
        elif code_lower == "ollama":
            return OllamaProvider()
        else:
            raise ValidationException(
                message=f"Unsupported AI Provider code: {code}",
                error_code="UNSUPPORTED_AI_PROVIDER",
            )

    async def route_model(self, organization_id: uuid.UUID, model_code: str) -> AIModel:
        """
        Intelligent routing mapping requested model code to active provider.
        Bypasses degraded providers if average error rates exceed 15%.
        """
        model = await self.model_repo.get_by_code(organization_id, model_code)
        if not model or model.status != "active":
            raise NotFoundException(message=f"Active AI model '{model_code}' not found.", error_code="MODEL_NOT_FOUND")

        # Resolve provider health
        health = await self.health_repo.get_latest_health(model.provider_id)
        if health and health.status == "offline" or (health and health.error_rate > 0.15):
            # Fallback routing logic: divert to local ollama or openai if claude/gemini degraded
            logger.warning("provider_degraded_initiating_fallback", provider=model.provider.code)
            fallback_code = "gpt-4o" if model_code != "gpt-4o" else "llama3"
            fallback_model = await self.model_repo.get_by_code(organization_id, fallback_code)
            if fallback_model and fallback_model.status == "active":
                return fallback_model

        return model

    async def chat(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        model_code: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_output: bool = False,
    ) -> dict[str, Any]:
        """Runs prompt completion and logs requests/responses with estimated cost metrics."""
        # 1. Route model
        model = await self.route_model(organization_id, model_code)
        provider_client = self._resolve_provider_client(model.provider.code)

        # 2. Process chat
        start_time = time.time()
        result = await provider_client.chat(
            messages=messages,
            model_code=model.code,
            temperature=temperature,
            max_tokens=max_tokens,
            json_output=json_output,
        )
        latency = int((time.time() - start_time) * 1000)

        # 3. Calculate Estimated cost
        prompt_cost = (result["prompt_tokens"] / 1_000_000) * model.cost_prompt_per_million
        completion_cost = (result["completion_tokens"] / 1_000_000) * model.cost_completion_per_million
        est_cost_cents = int((prompt_cost + completion_cost) * 100)

        # 4. Log AIRequest and AIResponse in database
        req = AIRequest(
            organization_id=organization_id,
            model_id=model.id,
            user_id=user_id,
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["prompt_tokens"] + result["completion_tokens"],
            estimated_cost_cents=est_cost_cents,
            latency_ms=latency,
            status="succeeded",
        )
        created_req = await self.request_repo.create(req)

        resp = AIResponse(
            organization_id=organization_id,
            request_id=created_req.id,
            response_text=result["response_text"],
            finish_reason=result["finish_reason"],
            raw_response={"model": model_code, "latency": latency, "provider": model.provider.code},
        )
        await self.response_repo.create(resp)

        # Increment usage metrics dynamically if billing/quota limit exists
        # Update provider average health checks latency
        await self._log_provider_health_check(model.provider_id, organization_id, latency, error=False)

        return {
            "response_text": result["response_text"],
            "total_tokens": req.total_tokens,
            "cost_cents": est_cost_cents,
            "model": model.code,
        }

    async def stream_chat(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        model_code: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_output: bool = False,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """SSE Streaming response chunks."""
        model = await self.route_model(organization_id, model_code)
        provider_client = self._resolve_provider_client(model.provider.code)

        # Run stream generator
        stream = provider_client.stream_chat(
            messages=messages,
            model_code=model.code,
            temperature=temperature,
            max_tokens=max_tokens,
            json_output=json_output,
        )

        async for chunk in stream:
            yield {
                "chunk_text": chunk["chunk_text"],
                "finish_reason": chunk["finish_reason"],
                "model": model.code,
            }

    async def _log_provider_health_check(
        self,
        provider_id: uuid.UUID,
        organization_id: uuid.UUID,
        latency: int,
        error: bool,
    ) -> None:
        """Write health metrics ledger details."""
        health = ProviderHealth(
            organization_id=organization_id,
            provider_id=provider_id,
            status="healthy" if not error else "degraded",
            error_rate=0.0 if not error else 1.0,
            latency_ms=latency,
        )
        await self.health_repo.create(health)

    async def seed_default_providers_and_models(self, organization_id: uuid.UUID) -> None:
        """Seed default providers registries and models context definitions."""
        providers_data = [
            ("OpenAI", "openai", "https://api.openai.com/v1", False),
            ("Google Gemini", "gemini", "https://generativelanguage.googleapis.com/v1", False),
            ("Anthropic Claude", "anthropic", "https://api.anthropic.com/v1", False),
            ("Local Ollama", "ollama", "http://localhost:11434/v1", True),
        ]

        seeded_provs = {}
        for name, code, url, custom in providers_data:
            existing = await self.provider_repo.get_by_code(organization_id, code)
            if not existing:
                prov = AIProvider(
                    organization_id=organization_id,
                    name=name,
                    code=code,
                    base_url=url,
                    is_custom=custom,
                    status="active",
                )
                prov = await self.provider_repo.create(prov)
                seeded_provs[code] = prov
            else:
                seeded_provs[code] = existing

        # Seed models
        models_data = [
            ("gpt-4o", "GPT-4o", "openai", 3000, 15000, 128000, {"vision": True, "tools": True}),
            ("gemini-1.5-pro", "Gemini 1.5 Pro", "gemini", 125, 375, 1000000, {"vision": True, "tools": True}),
            ("claude-3-5-sonnet", "Claude 3.5 Sonnet", "anthropic", 300, 1500, 200000, {"vision": True, "tools": True}),
            ("llama3", "Llama 3 (8B Local)", "ollama", 0, 0, 8192, {"vision": False, "tools": False}),
        ]

        for code, name, provider_code, cost_p, cost_c, context, cap in models_data:
            prov = seeded_provs.get(provider_code)
            if not prov:
                continue

            existing_model = await self.model_repo.get_by_code(organization_id, code)
            if not existing_model:
                model = AIModel(
                    organization_id=organization_id,
                    provider_id=prov.id,
                    name=name,
                    code=code,
                    version="latest",
                    capabilities=cap,
                    context_window=context,
                    cost_prompt_per_million=cost_p,
                    cost_completion_per_million=cost_c,
                    latency_ms_avg=1500,
                    status="active",
                )
                await self.model_repo.create(model)
            else:
                existing_model.cost_prompt_per_million = cost_p
                existing_model.cost_completion_per_million = cost_c
                await self.model_repo.update(existing_model)
