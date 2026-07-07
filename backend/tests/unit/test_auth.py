"""
Nexora Platform — Authentication Unit Tests
"""

from __future__ import annotations

from datetime import timedelta
import pytest

from app.core.exceptions import AuthenticationException, ValidationException
from app.utils.crypto import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_password_hashing() -> None:
    """Verify that password hashing hashes properly and verifies successfully."""
    pwd = "SecurePassword123!"
    hashed = hash_password(pwd)
    
    assert hashed != pwd
    assert hashed.startswith("$2b$")  # Bcrypt signature
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_password_strength_validation() -> None:
    """Test validation of password complexity requirements."""
    # Valid
    validate_password_strength("StrongPass123!")

    # Missing length
    with pytest.raises(ValidationException) as exc_info:
        validate_password_strength("Sh1!")
    assert exc_info.value.error_code == "PASSWORD_TOO_SHORT"

    # Missing uppercase
    with pytest.raises(ValidationException) as exc_info:
        validate_password_strength("weakpass123!")
    assert exc_info.value.error_code == "PASSWORD_NO_UPPERCASE"

    # Missing lowercase
    with pytest.raises(ValidationException) as exc_info:
        validate_password_strength("WEAKPASS123!")
    assert exc_info.value.error_code == "PASSWORD_NO_LOWERCASE"

    # Missing number
    with pytest.raises(ValidationException) as exc_info:
        validate_password_strength("WeakPassword!")
    assert exc_info.value.error_code == "PASSWORD_NO_DIGIT"

    # Missing special character
    with pytest.raises(ValidationException) as exc_info:
        validate_password_strength("WeakPassword123")
    assert exc_info.value.error_code == "PASSWORD_NO_SPECIAL"


def test_jwt_token_operations() -> None:
    """Verify token encoding, decoding, and type safeguards."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    claims = {"email": "test@nexora.tech", "org_id": "8fa110df-c2bb-41a4-b09e-71175653bfa1"}
    
    # Access token creation
    token = create_jwt_token(
        subject=user_id,
        expires_delta=timedelta(minutes=15),
        token_type="access",
        additional_claims=claims,
    )
    
    # Decoding success
    payload = decode_jwt_token(token, expected_type="access")
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert payload["email"] == claims["email"]
    assert payload["org_id"] == claims["org_id"]

    # Decoding error type mismatch
    with pytest.raises(AuthenticationException) as exc_info:
        decode_jwt_token(token, expected_type="refresh")
    assert exc_info.value.error_code == "INVALID_TOKEN_TYPE"
