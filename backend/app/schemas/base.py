"""
Nexora Platform — Base Pydantic Schemas

Provides standardized response envelopes and base schemas
that all API responses and requests should use.

All API responses are wrapped in an ApiResponse envelope
containing success status, message, data, errors, and metadata.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Generic type variable for response data
T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Base schema that all Pydantic schemas inherit from.

    Configured with:
    - from_attributes: Allows creating schemas from ORM model instances.
    - populate_by_name: Allows using field names or aliases.
    - str_strip_whitespace: Automatically strips whitespace from string fields.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class ResponseMeta(BaseSchema):
    """Metadata included in every API response."""

    request_id: str = Field(description="Correlation ID for request tracing")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Server timestamp when the response was generated",
    )


class ApiResponse(BaseSchema, Generic[T]):
    """
    Standard API response envelope.

    All API responses are wrapped in this structure for consistency.

    Attributes:
        success: Whether the operation was successful.
        message: Human-readable message describing the result.
        data: The response payload (typed via generic).
        errors: Error details if the operation failed.
        meta: Response metadata (request ID, timestamp).
    """

    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Human-readable result message")
    data: T | None = Field(default=None, description="Response payload")
    errors: list[ErrorDetail] | None = Field(default=None, description="Error details")
    meta: ResponseMeta = Field(description="Response metadata")


class ErrorDetail(BaseSchema):
    """Structured error detail for validation and domain errors."""

    field: str | None = Field(default=None, description="Field that caused the error")
    message: str = Field(description="Error description")
    error_code: str = Field(description="Machine-readable error code")


# Re-declare ApiResponse after ErrorDetail to resolve forward reference
ApiResponse.model_rebuild()


class PaginationMeta(BaseSchema):
    """Pagination metadata for list responses."""

    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Number of items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Paginated API response for list endpoints.

    Extends the standard response with pagination metadata.
    """

    success: bool = Field(default=True, description="Whether the operation succeeded")
    message: str = Field(default="Success", description="Human-readable result message")
    data: list[T] = Field(default_factory=list, description="List of items")
    pagination: PaginationMeta = Field(description="Pagination information")
    meta: ResponseMeta = Field(description="Response metadata")


class PaginationParams(BaseSchema):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate the SQL offset from page and page_size."""
        return (self.page - 1) * self.page_size


class EntityBase(BaseSchema):
    """
    Base schema for entity responses.

    Includes the standard fields from BaseModel.
    """

    id: UUID = Field(description="Entity unique identifier")
    organization_id: UUID = Field(description="Organization that owns this entity")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    created_by: UUID | None = Field(default=None, description="User who created this entity")
    updated_by: UUID | None = Field(default=None, description="User who last updated this entity")


def create_success_response(
    data: Any = None,
    message: str = "Success",
    request_id: str = "",
) -> dict[str, Any]:
    """
    Helper to create a standardized success response dict.

    Args:
        data: Response payload.
        message: Human-readable success message.
        request_id: Correlation ID for the request.

    Returns:
        Dictionary matching the ApiResponse schema.
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


def create_error_response(
    message: str = "An error occurred",
    errors: list[dict[str, Any]] | None = None,
    request_id: str = "",
) -> dict[str, Any]:
    """
    Helper to create a standardized error response dict.

    Args:
        message: Human-readable error message.
        errors: List of structured error details.
        request_id: Correlation ID for the request.

    Returns:
        Dictionary matching the ApiResponse schema.
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }

