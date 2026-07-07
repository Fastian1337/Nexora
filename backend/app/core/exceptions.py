"""
Nexora Platform — Domain Exceptions

Defines a hierarchy of domain-specific exceptions that map to HTTP status codes.
These exceptions are caught by the global error handler middleware and
converted to standardized API error responses.

Exception Hierarchy:
    NexoraException (base)
    ├── NotFoundException (404)
    ├── ValidationException (422)
    ├── AuthenticationException (401)
    ├── AuthorizationException (403)
    ├── ConflictException (409)
    ├── RateLimitException (429)
    └── ExternalServiceException (502)
"""

from __future__ import annotations

from typing import Any


class NexoraException(Exception):
    """
    Base exception for all Nexora domain exceptions.

    All domain-specific exceptions must inherit from this class
    to ensure they are properly caught by the global error handler.

    Attributes:
        message: Human-readable error message.
        error_code: Machine-readable error code for client-side handling.
        status_code: HTTP status code to return.
        details: Additional error context (e.g., field-level errors).
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(NexoraException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            details=details,
        )


class ValidationException(NexoraException):
    """Raised when input data fails validation."""

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=422,
            details=details,
        )


class AuthenticationException(NexoraException):
    """Raised when authentication fails (invalid or missing credentials)."""

    def __init__(
        self,
        message: str = "Authentication required",
        error_code: str = "AUTHENTICATION_FAILED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            details=details,
        )


class AuthorizationException(NexoraException):
    """Raised when the user lacks permission to perform an action."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=403,
            details=details,
        )


class ConflictException(NexoraException):
    """Raised when there is a data conflict (e.g., duplicate entry)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
            details=details,
        )


class RateLimitException(NexoraException):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=429,
            details=details,
        )


class ExternalServiceException(NexoraException):
    """Raised when an external service call fails."""

    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            details=details,
        )
