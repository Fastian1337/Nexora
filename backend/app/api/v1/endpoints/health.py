"""
Nexora Platform — Health Check Endpoints

Provides liveness and readiness probes for container orchestration
(Docker, Kubernetes) and monitoring systems.

Endpoints:
    GET /health       — Liveness probe (app is running)
    GET /health/ready — Readiness probe (app + dependencies are ready)
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis, get_settings_dep
from app.config.settings import Settings
from app.db.redis import check_redis_health
from app.schemas.health import (
    HealthCheckResponse,
    ReadinessCheckResponse,
    ServiceHealth,
)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthCheckResponse,
    summary="Liveness Probe",
    description="Returns 200 if the application is running. Used by container orchestrators.",
)
async def health_check(
    settings: Settings = Depends(get_settings_dep),
) -> HealthCheckResponse:
    """
    Basic liveness check.

    Returns the application status, version, and environment.
    Does not check external dependencies — that's what /ready is for.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/ready",
    response_model=ReadinessCheckResponse,
    summary="Readiness Probe",
    description="Checks the application and all dependencies (PostgreSQL, Redis). "
    "Returns 'ready' only if all services are reachable.",
)
async def readiness_check(
    settings: Settings = Depends(get_settings_dep),
    db: AsyncSession = Depends(get_db),
) -> ReadinessCheckResponse:
    """
    Readiness check with dependency health verification.

    Checks:
    - PostgreSQL: Executes a simple query
    - Redis: Sends a PING command

    Reports latency for each service.
    """
    services: dict[str, ServiceHealth] = {}

    # Check PostgreSQL
    db_start = time.monotonic()
    try:
        await db.execute(text("SELECT 1"))
        db_latency = (time.monotonic() - db_start) * 1000
        services["postgresql"] = ServiceHealth(
            status="healthy",
            latency_ms=round(db_latency, 2),
            message="Connection successful",
        )
    except Exception as e:
        db_latency = (time.monotonic() - db_start) * 1000
        services["postgresql"] = ServiceHealth(
            status="unhealthy",
            latency_ms=round(db_latency, 2),
            message=str(e),
        )

    # Check Redis
    redis_start = time.monotonic()
    try:
        redis_healthy = await check_redis_health()
        redis_latency = (time.monotonic() - redis_start) * 1000
        services["redis"] = ServiceHealth(
            status="healthy" if redis_healthy else "unhealthy",
            latency_ms=round(redis_latency, 2),
            message="Connection successful" if redis_healthy else "PING failed",
        )
    except Exception as e:
        redis_latency = (time.monotonic() - redis_start) * 1000
        services["redis"] = ServiceHealth(
            status="unhealthy",
            latency_ms=round(redis_latency, 2),
            message=str(e),
        )

    # Determine overall status
    all_healthy = all(svc.status == "healthy" for svc in services.values())
    overall_status = "ready" if all_healthy else "degraded"

    return ReadinessCheckResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.app_env,
        services=services,
    )
