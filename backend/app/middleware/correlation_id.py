"""
Nexora Platform — Correlation ID Middleware

Generates or extracts a UUID correlation ID for every request.
The ID is propagated through structlog context vars so it appears
in all log entries for that request.

The correlation ID is also returned in the response headers,
enabling end-to-end request tracing across services.
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import CORRELATION_ID_HEADER


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique correlation ID to each request.

    If the client provides an X-Correlation-ID header, it is reused.
    Otherwise, a new UUID4 is generated.

    The correlation ID is:
    1. Set in structlog context vars (available in all log entries)
    2. Stored on the request state (accessible in endpoints)
    3. Returned in the response header
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the request and attach a correlation ID."""
        # Extract existing or generate new correlation ID
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER,
            str(uuid.uuid4()),
        )

        # Store on request state for endpoint access
        request.state.correlation_id = correlation_id

        # Bind to structlog context for automatic inclusion in logs
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
        )

        # Process request
        response = await call_next(request)

        # Include correlation ID in response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response
