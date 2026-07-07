"""
Nexora Platform — Authentication Routing Endpoints

Declares all endpoints managing user authentication lifecycle, registration,
login (with cookie management), session rotation, resets, and verification.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.deps import get_auth_service, get_current_user
from app.config.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.schemas.base import ApiResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Registers a new account and returns the user details.
    Triggers email verification verification token generation.
    """
    user = await auth_service.register(payload)
    correlation_id = getattr(request.state, "correlation_id", "")
    
    # Map to schema response
    data = UserResponse.model_validate(user)
    return {
        "success": True,
        "message": "User registered successfully. Please verify your email.",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate credentials",
)
async def login(
    response: Response,
    request: Request,
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Verifies user credentials. On success, issues JWT access and refresh tokens.
    Refresh token is saved securely in HTTP-only cookies.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = await auth_service.login(payload, client_ip, user_agent)
    correlation_id = getattr(request.state, "correlation_id", "")

    # Set HTTP-only secure cookie for the refresh token
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60 if payload.remember_me else 7 * 24 * 60 * 60,
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": tokens,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Invalidate active session",
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Logs out the user, blocklists the active refresh token, and deletes the cookie.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        await auth_service.logout(refresh_token)
        response.delete_cookie(key="refresh_token")

    return {
        "success": True,
        "message": "Logout successful",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate active tokens",
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Performs refresh token rotation. Reads the refresh token from cookies,
    verifies validity, and issues a fresh rotated token pair.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        # Fallback to authorization header if cookies are blocked
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ")[1]

    if not refresh_token:
        from app.core.exceptions import AuthenticationException
        raise AuthenticationException(
            message="Refresh token is missing",
            error_code="MISSING_REFRESH_TOKEN",
        )

    new_tokens = await auth_service.rotate_tokens(refresh_token)

    # Set new HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=new_tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return {
        "success": True,
        "message": "Tokens rotated successfully",
        "data": new_tokens,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/forgot-password",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Initiates password recovery. Generates a secure recovery token.
    (Email delivery is logged/mocked in Phase 1).
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    reset_token = await auth_service.forgot_password(payload.email)
    
    # In production, we'd trigger an email workflow with the reset_token
    # Log the token in development for testing convenience
    logger.info("password_reset_email_trigger", email=payload.email, token=reset_token)

    return {
        "success": True,
        "message": "If the account exists, a password reset link has been sent.",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/reset-password",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Validates a password reset token and updates the user's password hash.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await auth_service.reset_password(payload.token, payload.new_password)

    return {
        "success": True,
        "message": "Password has been reset successfully.",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/change-password",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Change password in session",
)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Updates the user's password. Requires active token authorization.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await auth_service.change_password(
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )

    return {
        "success": True,
        "message": "Password changed successfully.",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/verify-email",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Verify email address",
)
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Verifies user email verification token.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await auth_service.verify_email(payload.token)

    return {
        "success": True,
        "message": "Email verified successfully.",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/resend-verification",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Resend verification email link",
)
async def resend_verification(
    request: Request,
    payload: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Generates and logs a new email verification token for the given account.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    # Check if account is valid
    user = await auth_service.user_repository.get_by_email(payload.email)
    if user:
        if user.email_verified:
            from app.core.exceptions import ValidationException
            raise ValidationException(
                message="Email is already verified",
                error_code="EMAIL_ALREADY_VERIFIED",
            )
        verification_token = await auth_service.generate_email_verification_token(payload.email)
        logger.info("resending_email_verification_token", email=payload.email, token=verification_token)

    return {
        "success": True,
        "message": "If the account exists and is unverified, a verification link has been resent.",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user context",
)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Returns user details of the currently authenticated bearer token.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    data = UserResponse.model_validate(current_user)

    return {
        "success": True,
        "message": "User details fetched successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }
