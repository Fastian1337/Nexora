"""
Nexora Platform — Structured Logging Configuration

Configures structlog for structured JSON logging in production
and human-readable console output in development.

The logger automatically includes:
- Timestamps (ISO 8601)
- Log level
- Logger name
- Correlation ID (from request context)

Usage:
    from app.config.logging import setup_logging, get_logger

    setup_logging(log_level="INFO", log_format="json")
    logger = get_logger(__name__)
    logger.info("message", key="value")
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format — 'json' for production, 'console' for development.
    """
    # Shared processors for all log entries
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        # Production: JSON output for log aggregation
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        # Development: Colorful console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to route through structlog
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
        force=True,
    )

    # Suppress noisy third-party loggers
    for noisy_logger in [
        "uvicorn.access",
        "uvicorn.error",
        "sqlalchemy.engine",
        "httpcore",
        "httpx",
        "asyncio",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str | None = None, **initial_context: Any) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__).
        **initial_context: Initial context key-value pairs bound to the logger.

    Returns:
        BoundLogger: A structured logger instance.
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    if initial_context:
        logger = logger.bind(**initial_context)
    return logger
