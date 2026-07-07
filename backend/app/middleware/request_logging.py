"""
Nexora Platform — Request Logging Middleware

Logs structured information about every HTTP request and response:
- Method, path, query parameters
- Response status code
- Request duration in milliseconds
- Client IP address
- Correlation ID (from CorrelationIdMiddleware)

This provides observability without application-level instrumentation.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs structured request/response information.

    Logs are emitted at INFO level for successful requests (2xx/3xx)
    and WARNING level for client/server errors (4xx/5xx).

    Health check endpoints are logged at DEBUG level to reduce noise.
    """

    # Paths to log at DEBUG level (high-frequency, low-value)
    _quiet_paths: set[str] = {"/api/v1/health", "/api/v1/health/ready"}

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the request and log timing information."""
        start_time = time.monotonic()

        # Extract request metadata
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else None
        client_ip = request.client.host if request.client else "unknown"

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.monotonic() - start_time) * 1000, 2)
        status_code = response.status_code

        # Build log context
        log_context = {
            "method": method,
            "path": path,
            "query": query,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        }

        # Choose log level based on path and status
        if path in self._quiet_paths:
            logger.debug("http_request", **log_context)
        elif status_code >= 500:
            logger.error("http_request", **log_context)
        elif status_code >= 400:
            logger.warning("http_request", **log_context)
        else:
            logger.info("http_request", **log_context)

        return response
