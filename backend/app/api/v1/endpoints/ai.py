"""
Nexora Platform — AI Gateway & Model Registry API Router Endpoints
"""

from __future__ import annotations

import json
import uuid
from typing import Any
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.deps import get_ai_gateway, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.ai_gateway import AIProvider, AIModel, AIRequest, ProviderHealth
from app.schemas.base import ApiResponse
from app.schemas.ai_gateway import (
    AIProviderResponse,
    AIModelResponse,
    ChatRequest,
    ChatResponse,
    HealthCheckResponse,
    TokenUsageResponse,
)
from app.services.ai.gateway import AiGateway

router = APIRouter(prefix="/ai", tags=["AI Gateway & Model Management"])


@router.get(
    "/providers",
    response_model=ApiResponse[list[AIProviderResponse]],
    status_code=status.HTTP_200_OK,
    summary="List active AI providers",
)
async def list_providers(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Returns AI providers registers scoped by organization tenant.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    providers = await ai_gateway.provider_repo.list_active(active_org.id)
    data = [AIProviderResponse.model_validate(p) for p in providers]
    return {
        "success": True,
        "message": "AI Providers list retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/models",
    response_model=ApiResponse[list[AIModelResponse]],
    status_code=status.HTTP_200_OK,
    summary="List registered AI Models",
)
async def list_models(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Returns registered models parameters scoped by organization.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    query = select(AIModel).where(AIModel.organization_id == active_org.id, AIModel.status == "active")
    result = await ai_gateway.model_repo.session.execute(query)
    models = result.scalars().all()
    data = [AIModelResponse.model_validate(m) for m in models]
    return {
        "success": True,
        "message": "AI Models list retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/chat",
    response_model=ApiResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Execute standard AI prompt",
)
async def chat_completion(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Routes chat completion payload to AI provider and logs estimated costs.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    # Map ChatMessage schema to list[dict]
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in payload.messages]
    
    result = await ai_gateway.chat(
        organization_id=active_org.id,
        user_id=current_user.id,
        model_code=payload.model_code,
        messages=messages_dict,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        json_output=payload.json_output,
    )

    data = ChatResponse(
        response_text=result["response_text"],
        total_tokens=result["total_tokens"],
        cost_cents=result["cost_cents"],
        model=result["model"],
    )

    return {
        "success": True,
        "message": "AI request completed",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream AI chunks completions",
)
async def stream_chat_completion(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> StreamingResponse:
    """
    Streams AI completion chunks using SSE (Server-Sent Events) formatting.
    """
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in payload.messages]
    
    async def event_generator():
        stream = await ai_gateway.stream_chat(
            organization_id=active_org.id,
            user_id=current_user.id,
            model_code=payload.model_code,
            messages=messages_dict,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            json_output=payload.json_output,
        )
        async for chunk in stream:
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post(
    "/test",
    response_model=ApiResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Run template test executions",
)
async def test_prompt(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Sends mock prompt variables test payload.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in payload.messages]
    
    result = await ai_gateway.chat(
        organization_id=active_org.id,
        user_id=current_user.id,
        model_code=payload.model_code,
        messages=messages_dict,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        json_output=payload.json_output,
    )

    data = ChatResponse(
        response_text=result["response_text"],
        total_tokens=result["total_tokens"],
        cost_cents=result["cost_cents"],
        model=result["model"],
    )

    return {
        "success": True,
        "message": "AI template test run succeeded",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/usage",
    response_model=ApiResponse[list[TokenUsageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Monitor Token Usage & Cost telemetry",
)
async def get_usage(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Returns AI request costs histories logs.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    query = select(AIRequest).where(AIRequest.organization_id == active_org.id).order_by(AIRequest.created_at.desc())
    result = await ai_gateway.request_repo.session.execute(query)
    reqs = result.scalars().all()
    data = [TokenUsageResponse.model_validate(r) for r in reqs]
    return {
        "success": True,
        "message": "Token usage records list retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/health",
    response_model=ApiResponse[list[HealthCheckResponse]],
    status_code=status.HTTP_200_OK,
    summary="List providers latencies and health checkpoints",
)
async def get_health(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    ai_gateway: AiGateway = Depends(get_ai_gateway),
) -> dict:
    """
    Returns providers latency stats and healthy check listings.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    query = select(ProviderHealth).where(ProviderHealth.organization_id == active_org.id).order_by(ProviderHealth.last_checked_at.desc())
    result = await ai_gateway.health_repo.session.execute(query)
    healths = result.scalars().all()
    data = [HealthCheckResponse.model_validate(h) for h in healths]
    return {
        "success": True,
        "message": "Provider health list retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }
