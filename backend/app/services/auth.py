"""
Nexora Platform — Authentication Service

Coordinates core use cases for auth, password checks, token creation,
revocation tracking in Redis, failed attempt lockouts, and session logging.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from redis.asyncio import Redis

from app.config.logging import get_logger
from app.config.settings import Settings
from app.core.exceptions import AuthenticationException, ConflictException, NotFoundException, ValidationException
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.crypto import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    validate_password_strength,
    verify_password,
)

logger = get_logger(__name__)


class AuthService:
    """
    Orchestrates authentication workflow logic.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        redis_client: Redis,
        settings: Settings,
    ) -> None:
        self.user_repository = user_repository
        self.redis = redis_client
        self.settings = settings

    async def register(self, payload: RegisterRequest) -> User:
        """
        Register a new user account.
        Validates password strength, checks email/username uniqueness,
        and assigns a default organization identifier.
        """
        # Validate password strength
        validate_password_strength(payload.password)

        # Check email uniqueness
        existing_email = await self.user_repository.get_by_email(payload.email)
        if existing_email:
            raise ConflictException(
                message="Account with this email already exists",
                error_code="EMAIL_EXISTS",
            )

        # Check username uniqueness
        existing_username = await self.user_repository.get_by_username(payload.username)
        if existing_username:
            raise ConflictException(
                message="Username is already taken",
                error_code="USERNAME_TAKEN",
            )

        # Hash password
        password_hash = hash_password(payload.password)

        # Create user record with a mock organization_id to satisfy DB constraint
        mock_org_id = uuid.uuid4()
        user = User(
            organization_id=mock_org_id,
            email=payload.email.lower(),
            username=payload.username.lower(),
            password_hash=password_hash,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
            status="active",
            email_verified=False,
            is_active=True,
            failed_login_attempts=0,
        )

        created_user = await self.user_repository.create(user)
        logger.info("user_registered", user_id=str(created_user.id), email=created_user.email)

        # Generate email verification token in background
        await self.generate_email_verification_token(created_user.email)

        return created_user

    async def login(self, payload: LoginRequest, ip_address: str | None, user_agent: str | None) -> TokenResponse:
        """
        Authenticate a user.
        Validates lock status, increments failed login counts, verifies credentials,
        and returns access/refresh tokens.
        """
        # Check by email or username
        user = await self.user_repository.get_by_email(payload.email)
        if not user:
            user = await self.user_repository.get_by_username(payload.email)

        if not user:
            raise AuthenticationException(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        # Check account locking
        if user.account_locked_until:
            now = datetime.now(timezone.utc)
            if user.account_locked_until > now:
                remaining_time = int((user.account_locked_until - now).total_seconds() / 60)
                raise AuthenticationException(
                    message=f"Account is temporarily locked. Try again in {remaining_time} minutes",
                    error_code="ACCOUNT_LOCKED",
                )
            else:
                # Lock has expired, reset failed attempts
                await self.user_repository.reset_failed_logins(user)

        # Verify password
        if not verify_password(payload.password, user.password_hash):
            # Increment failed count, lock if needed
            await self.user_repository.increment_failed_login(
                user=user,
                max_attempts=5,
                lock_duration_minutes=15,
            )
            logger.warning("failed_login_attempt", user_id=str(user.id), email=user.email, ip=ip_address)
            raise AuthenticationException(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        # Reset failed attempts on success
        await self.user_repository.reset_failed_logins(user)

        # Update last login info
        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repository.update(user)

        logger.info("user_logged_in", user_id=str(user.id), email=user.email, ip=ip_address)

        # Issue tokens
        return await self._issue_tokens(user, payload.remember_me)

    async def logout(self, refresh_token: str) -> None:
        """
        Revoke refresh token by adding it to Redis blocklist.
        """
        try:
            payload = decode_jwt_token(refresh_token, expected_type="refresh")
            token_id = payload.get("sub")
            exp = payload.get("exp")
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now) if exp else 3600

            if ttl > 0:
                # Add token to blocklist in Redis
                await self.redis.set(f"revoked_token:{refresh_token}", "1", ex=ttl)
                logger.info("user_logged_out", token_sub=token_id)
        except AuthenticationException:
            # Token already invalid or expired, ignore
            pass

    async def rotate_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Perform refresh token rotation.
        Validates token, ensures it is not revoked, issues a new token pair,
        and invalidates the old one.
        """
        # Check if revoked
        if await self.redis.get(f"revoked_token:{refresh_token}"):
            raise AuthenticationException(
                message="Token has been revoked",
                error_code="REVOKED_TOKEN",
            )

        # Decode token
        payload = decode_jwt_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")

        # Fetch user
        user = await self.user_repository.get_by_id(uuid.UUID(user_id), mock_org_id := uuid.UUID(payload.get("org_id", str(uuid.uuid4()))))
        if not user or not user.is_active:
            raise AuthenticationException(
                message="User account is deactivated",
                error_code="USER_INACTIVE",
            )

        # Revoke the old token
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now) if exp else 3600
        if ttl > 0:
            await self.redis.set(f"revoked_token:{refresh_token}", "1", ex=ttl)

        # Issue new token pair
        return await self._issue_tokens(user, remember_me=True)

    async def generate_email_verification_token(self, email: str) -> str:
        """
        Create a secure email verification token and cache in Redis for 24h.
        """
        token = uuid.uuid4().hex
        # Cache token to email mapping
        await self.redis.set(f"token:email_verify:{token}", email, ex=86400) # 24 hours
        logger.info("email_verification_token_generated", email=email)
        return token

    async def verify_email(self, token: str) -> None:
        """
        Verify account email using cached token.
        """
        email = await self.redis.get(f"token:email_verify:{token}")
        if not email:
            raise ValidationException(
                message="Verification token has expired or is invalid",
                error_code="INVALID_VERIFICATION_TOKEN",
            )

        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(message="User not found", error_code="USER_NOT_FOUND")

        await self.user_repository.verify_email(user)
        await self.redis.delete(f"token:email_verify:{token}")
        logger.info("email_verified", user_id=str(user.id), email=email)

    async def forgot_password(self, email: str) -> str:
        """
        Initiate password recovery flow.
        Generates and caches a single-use token in Redis for 1 hour.
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Silently succeed to prevent account enumeration
            logger.info("forgot_password_ignored_nonexistent_email", email=email)
            return ""

        token = uuid.uuid4().hex
        await self.redis.set(f"token:password_reset:{token}", email, ex=3600) # 1 hour
        logger.info("password_reset_token_issued", user_id=str(user.id), email=email)
        return token

    async def reset_password(self, token: str, password_payload: str) -> None:
        """
        Update user password using reset token validation.
        """
        email = await self.redis.get(f"token:password_reset:{token}")
        if not email:
            raise ValidationException(
                message="Password reset token has expired or is invalid",
                error_code="INVALID_RESET_TOKEN",
            )

        validate_password_strength(password_payload)

        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(message="User not found", error_code="USER_NOT_FOUND")

        user.password_hash = hash_password(password_payload)
        await self.user_repository.update(user)

        # Evict token
        await self.redis.delete(f"token:password_reset:{token}")
        logger.info("password_reset_successful", user_id=str(user.id), email=email)

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """
        Change user password in active session.
        """
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationException(
                message="Incorrect current password",
                error_code="INCORRECT_PASSWORD",
            )

        validate_password_strength(new_password)

        user.password_hash = hash_password(new_password)
        await self.user_repository.update(user)
        logger.info("password_changed_by_user", user_id=str(user.id))

    async def _issue_tokens(self, user: User, remember_me: bool) -> TokenResponse:
        """
        Internal utility to generate access/refresh token pair.
        """
        access_lifetime = timedelta(minutes=15)
        refresh_lifetime = timedelta(days=30 if remember_me else 7)

        additional_claims = {
            "email": user.email,
            "username": user.username,
            "org_id": str(user.organization_id),
        }

        access_token = create_jwt_token(
            subject=str(user.id),
            expires_delta=access_lifetime,
            token_type="access",
            additional_claims=additional_claims,
        )

        refresh_token = create_jwt_token(
            subject=str(user.id),
            expires_delta=refresh_lifetime,
            token_type="refresh",
            additional_claims={"org_id": str(user.organization_id)},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_lifetime.total_seconds()),
        )
