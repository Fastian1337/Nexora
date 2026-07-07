"""
Nexora Platform — Cryptographic, Hashing & Token Utilities

Handles password hashing (bcrypt), password complexity validation,
and JWT generation, signing, and verification.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config.logging import get_logger
from app.config.settings import get_settings
from app.core.exceptions import AuthenticationException, ValidationException

logger = get_logger(__name__)
settings = get_settings()

# Password complexity regex rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_UPPERCASE_RE = re.compile(r"[A-Z]")
PASSWORD_LOWERCASE_RE = re.compile(r"[a-z]")
PASSWORD_DIGIT_RE = re.compile(r"\d")
PASSWORD_SPECIAL_RE = re.compile(r"[!@#$%^&*(),.?\":{}|<>]")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash.

    Returns:
        str: Hashed password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password: Plaintext password.
        hashed_password: Hashed password to verify against.

    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error("password_verification_error", error=str(e))
        return False


def validate_password_strength(password: str) -> None:
    """
    Validate that a password meets complexity rules.

    Rules:
    - Minimum length
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character

    Raises:
        ValidationException: If password doesn't meet requirements.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationException(
            message=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long",
            error_code="PASSWORD_TOO_SHORT",
        )

    if not PASSWORD_UPPERCASE_RE.search(password):
        raise ValidationException(
            message="Password must contain at least one uppercase letter",
            error_code="PASSWORD_NO_UPPERCASE",
        )

    if not PASSWORD_LOWERCASE_RE.search(password):
        raise ValidationException(
            message="Password must contain at least one lowercase letter",
            error_code="PASSWORD_NO_LOWERCASE",
        )

    if not PASSWORD_DIGIT_RE.search(password):
        raise ValidationException(
            message="Password must contain at least one number",
            error_code="PASSWORD_NO_DIGIT",
        )

    if not PASSWORD_SPECIAL_RE.search(password):
        raise ValidationException(
            message="Password must contain at least one special character",
            error_code="PASSWORD_NO_SPECIAL",
        )


def create_jwt_token(
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Generate and sign a JSON Web Token.

    Args:
        subject: The subject of the token (typically user ID).
        expires_delta: How long the token is valid for.
        token_type: The type of token ('access' or 'refresh').
        additional_claims: Optional key-value pairs to include in payload.

    Returns:
        str: Encoded JWT.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_jwt_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """
    Decode and verify a JSON Web Token.

    Args:
        token: The encoded token string.
        expected_type: Optional expected token type (e.g. 'access', 'refresh').

    Returns:
        dict: The decoded token payload.

    Raises:
        AuthenticationException: If signature is invalid, token expired, or type mismatches.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        
        # Check token type if expected
        if expected_type and payload.get("type") != expected_type:
            raise AuthenticationException(
                message=f"Invalid token type: expected {expected_type}",
                error_code="INVALID_TOKEN_TYPE",
            )
            
        return payload
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationException(message="Token signature has expired", error_code="TOKEN_EXPIRED") from e
    except jwt.InvalidTokenError as e:
        raise AuthenticationException(message="Token signature is invalid", error_code="INVALID_TOKEN") from e
