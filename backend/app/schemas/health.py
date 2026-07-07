"""
Nexora Platform — Health Check Schemas

Pydantic models for health check endpoint responses.
"""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import BaseSchema


class ServiceHealth(BaseSchema):
    """Health status of an individual service dependency."""

    status: str = Field(description="Service status: 'healthy' or 'unhealthy'")
    latency_ms: float | None = Field(default=None, description="Response latency in milliseconds")
    message: str | None = Field(default=None, description="Additional status information")


class HealthCheckResponse(BaseSchema):
    """Response for the basic health check endpoint."""

    status: str = Field(description="Overall application status")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current environment (development/staging/production)")


class ReadinessCheckResponse(BaseSchema):
    """Response for the readiness probe endpoint with dependency status."""

    status: str = Field(description="Overall readiness status")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current environment")
    services: dict[str, ServiceHealth] = Field(
        description="Health status of each service dependency"
    )
