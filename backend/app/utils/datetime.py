"""
Nexora Platform — DateTime Utilities

Provides timezone-aware datetime helpers to ensure consistent
timestamp handling across the application.

All timestamps in Nexora should be UTC. These utilities ensure
that datetime objects are always timezone-aware.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Get the current UTC datetime (timezone-aware).

    Returns:
        datetime: Current UTC datetime with tzinfo set.
    """
    return datetime.now(tz=timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    If the datetime is naive (no tzinfo), it is assumed to be UTC.
    If it has tzinfo, it is converted to UTC.

    Args:
        dt: The datetime to convert.

    Returns:
        datetime: The datetime in UTC with tzinfo set.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_iso(dt: datetime) -> str:
    """
    Format a datetime as an ISO 8601 string.

    Args:
        dt: The datetime to format.

    Returns:
        str: ISO 8601 formatted string.
    """
    return dt.isoformat()


def parse_iso(dt_string: str) -> datetime:
    """
    Parse an ISO 8601 string into a timezone-aware datetime.

    Args:
        dt_string: ISO 8601 formatted string.

    Returns:
        datetime: Parsed datetime (UTC if no timezone specified).
    """
    dt = datetime.fromisoformat(dt_string)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
