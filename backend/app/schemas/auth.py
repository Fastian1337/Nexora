"""
Nexora Platform — Authentication Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    """Schema for user registration."""

    email: EmailStr = Field(description="User's email address")
    username: str = Field(min_length=3, max_length=50, description="Unique username")
    password: str = Field(min_length=8, description="Cleartext password meeting complexity criteria")
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=50)


class LoginRequest(BaseSchema):
    """Schema for user login credentials."""

    email: str = Field(description="Username or email address")
    password: str = Field(description="User password")
    remember_me: bool = Field(default=False, description="Extend session duration if true")


class TokenResponse(BaseSchema):
    """Schema containing JWT tokens returned on successful auth."""

    access_token: str = Field(description="Access token string (JWT)")
    refresh_token: str = Field(description="Refresh token string (JWT)")
    token_type: str = Field(default="bearer", description="Token schema type")
    expires_in: int = Field(description="Access token lifespan in seconds")


class UserResponse(BaseSchema):
    """Schema representing basic user metadata returned by auth endpoints."""

    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    profile_photo_url: str | None
    status: str
    email_verified: bool
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ForgotPasswordRequest(BaseSchema):
    """Request schema to initiate password recovery email."""

    email: EmailStr = Field(description="Account email to recover")


class ResetPasswordRequest(BaseSchema):
    """Request schema containing the recovery token and new password."""

    token: str = Field(description="Secure single-use reset token")
    new_password: str = Field(min_length=8, description="New password")


class ChangePasswordRequest(BaseSchema):
    """Request schema for active session password rotation."""

    current_password: str = Field(description="Existing account password")
    new_password: str = Field(min_length=8, description="New password")


class VerifyEmailRequest(BaseSchema):
    """Request schema containing verification token details."""

    token: str = Field(description="Secure verification token sent to email")


class ResendVerificationRequest(BaseSchema):
    """Request schema to request another email verification token."""

    email: EmailStr = Field(description="Email of account to verify")
