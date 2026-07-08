"""
Nexora Platform — Organization Pydantic v2 Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class OrganizationBase(BaseSchema):
    name: str = Field(min_length=2, max_length=255, description="Official business name")
    business_type: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    company_size: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default="UTC", max_length=100)
    language: str | None = Field(default="en", max_length=100)
    currency: str | None = Field(default="USD", max_length=10)


class OrganizationCreate(OrganizationBase):
    slug: str = Field(min_length=2, max_length=255, description="Unique URL identifier segment")


class OrganizationUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    business_type: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    company_size: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)
    language: str | None = Field(default=None, max_length=100)
    currency: str | None = Field(default=None, max_length=10)
    logo_url: str | None = Field(default=None, max_length=1024)
    brand_colors: dict[str, Any] | None = Field(default=None)


class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    slug: str
    status: str
    owner_id: uuid.UUID | None
    logo_url: str | None
    brand_colors: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class OrganizationSettingsUpdate(BaseSchema):
    theme: str | None = Field(default=None, max_length=50)
    brand_colors: dict[str, Any] | None = Field(default=None)
    logo_url: str | None = Field(default=None, max_length=1024)
    business_hours: dict[str, Any] | None = Field(default=None)
    working_days: list[str] | None = Field(default=None)
    languages: list[str] | None = Field(default=None)
    voice_language: str | None = Field(default=None, max_length=50)
    ai_personality: str | None = Field(default=None, max_length=1000)
    notification_preferences: dict[str, Any] | None = Field(default=None)
    whatsapp_settings: dict[str, Any] | None = Field(default=None)
    email_settings: dict[str, Any] | None = Field(default=None)
    social_media_accounts: dict[str, Any] | None = Field(default=None)
    custom_domain: str | None = Field(default=None, max_length=255)


class OrganizationSettingsResponse(OrganizationSettingsUpdate):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OrganizationMemberResponse(BaseSchema):
    membership_id: uuid.UUID
    user_id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str | None
    last_name: str | None
    role: str
    joined_at: datetime


class OrganizationInvitationCreate(BaseSchema):
    email: EmailStr
    role: str = Field(default="employee", description="Target role in tenant organization")


class OrganizationInvitationResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: str
    token: str
    status: str
    expires_at: datetime
    invited_by: uuid.UUID
    created_at: datetime


class OrganizationSwitchRequest(BaseSchema):
    organization_id: uuid.UUID
