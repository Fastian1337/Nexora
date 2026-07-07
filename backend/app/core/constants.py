"""
Nexora Platform — Application Constants

Centralized constants used throughout the application.
These values should NOT be configurable via environment variables
as they represent fixed application behavior.
"""

from __future__ import annotations

# -------------------- API --------------------
API_V1_PREFIX: str = "/api/v1"
API_TITLE: str = "Nexora AI Employee Platform"
API_DESCRIPTION: str = (
    "Enterprise-grade SaaS platform for AI-powered business automation. "
    "Automates customer support, voice calls, appointments, marketing, "
    "sales, and internal operations."
)

# -------------------- Pagination --------------------
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100
MIN_PAGE_SIZE: int = 1

# -------------------- Health Check --------------------
HEALTH_CHECK_TIMEOUT_SECONDS: int = 5

# -------------------- Request --------------------
CORRELATION_ID_HEADER: str = "X-Correlation-ID"
MAX_REQUEST_BODY_SIZE: int = 10 * 1024 * 1024  # 10 MB

# -------------------- Multi-Tenancy --------------------
ORGANIZATION_HEADER: str = "X-Organization-ID"

# -------------------- Date/Time --------------------
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT: str = "%Y-%m-%d"
