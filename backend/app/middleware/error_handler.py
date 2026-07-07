"""
Nexora Platform — Global Exception Handler

Catches all exceptions and converts them to standardized API error
responses. Distinguishes between:

1. Domain exceptions (NexoraException hierarchy) → mapped status codes
2. Pydantic validation errors → 422
3. Unhandled exceptions → 500 (details hidden in production)

This ensures the client always receives a consistent error format
regardless of where the error occurred.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config.logging import get_logger
from app.config.settings import get_settings
from app.core.exceptions import NexoraException
from app.schemas.base import create_error_response

logger = get_logger(__name__)


async def nexora_exception_handler(request: Request, exc: NexoraException) -> JSONResponse:
    """
    Handle domain-specific exceptions.

    Maps the exception's status_code and error_code to a standard response.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    logger.warning(
        "domain_exception",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=exc.message,
            errors=[
                {
                    "field": None,
                    "message": exc.message,
                    "error_code": exc.error_code,
                }
            ],
            request_id=correlation_id,
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI/Pydantic request validation errors.

    Converts Pydantic validation errors into a structured error
    response with field-level detail.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    errors = []
    for error in exc.errors():
        field_path = " → ".join(str(loc) for loc in error.get("loc", []))
        errors.append(
            {
                "field": field_path,
                "message": error.get("msg", "Validation error"),
                "error_code": "VALIDATION_ERROR",
            }
        )

    logger.warning(
        "validation_error",
        error_count=len(errors),
        errors=errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            message="Request validation failed",
            errors=errors,
            request_id=correlation_id,
        ),
    )


async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic V2 validation errors raised outside FastAPI.

    These can occur when manually validating data in services.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    errors = []
    for error in exc.errors():
        field_path = " → ".join(str(loc) for loc in error.get("loc", []))
        errors.append(
            {
                "field": field_path,
                "message": error.get("msg", "Validation error"),
                "error_code": "VALIDATION_ERROR",
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            message="Data validation failed",
            errors=errors,
            request_id=correlation_id,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions.

    In development: includes the exception message for debugging.
    In production: returns a generic error message to avoid leaking internals.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    settings = get_settings()

    logger.exception(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )

    # Only expose error details in non-production environments
    if settings.is_production:
        message = "An unexpected error occurred. Please try again later."
    else:
        message = f"{type(exc).__name__}: {exc}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            message=message,
            errors=[
                {
                    "field": None,
                    "message": message,
                    "error_code": "INTERNAL_ERROR",
                }
            ],
            request_id=correlation_id,
        ),
    )
