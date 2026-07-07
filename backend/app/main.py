"""
Nexora Platform — Application Entry Point

Creates and configures the FastAPI application using the factory pattern.
Manages the full application lifecycle including:

- Database connection initialization and teardown
- Redis connection initialization and teardown
- Middleware registration
- Exception handler registration
- Router registration
- CORS configuration
- Structured logging setup

Usage:
    Development:  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    Production:   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.v1.router import router as v1_router
from app.config.logging import get_logger, setup_logging
from app.config.settings import get_settings
from app.core.constants import API_DESCRIPTION, API_TITLE, API_V1_PREFIX
from app.core.exceptions import NexoraException
from app.db.redis import close_redis, init_redis
from app.db.session import close_engine, init_engine, init_session_factory
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.error_handler import (
    nexora_exception_handler,
    pydantic_validation_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware.request_logging import RequestLoggingMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize DB engine, session factory, Redis
    - Shutdown: Close DB connections, Redis connections
    """
    settings = get_settings()

    # ---- Startup ----
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    # Initialize database
    init_engine()
    init_session_factory()
    logger.info("database_initialized")

    # Initialize Redis
    init_redis()
    logger.info("redis_initialized")

    logger.info("application_started")

    yield

    # ---- Shutdown ----
    logger.info("application_shutting_down")

    await close_engine()
    await close_redis()

    logger.info("application_stopped")


def create_application() -> FastAPI:
    """
    Application factory.

    Creates and fully configures the FastAPI application.

    Returns:
        FastAPI: The configured application instance.
    """
    settings = get_settings()

    # Setup structured logging
    setup_logging(
        log_level=settings.app_log_level,
        log_format=settings.app_log_format,
    )

    # Create FastAPI app
    application = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=settings.app_version,
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ---- Register Exception Handlers ----
    application.add_exception_handler(NexoraException, nexora_exception_handler)  # type: ignore[arg-type]
    application.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    application.add_exception_handler(ValidationError, pydantic_validation_handler)  # type: ignore[arg-type]
    application.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # ---- Register Middleware (order matters — first added = outermost) ----
    # CORS must be the outermost middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )

    # Correlation ID is added before logging so logs include the ID
    application.add_middleware(CorrelationIdMiddleware)

    # Request logging captures timing and status
    application.add_middleware(RequestLoggingMiddleware)

    # ---- Register Routers ----
    application.include_router(v1_router, prefix=API_V1_PREFIX)

    return application


# Create the application instance
app = create_application()
