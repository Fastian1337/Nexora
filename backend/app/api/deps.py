"""
Nexora Platform — Dependency Injection Providers

FastAPI dependencies for injecting shared resources into endpoints.
These providers ensure consistent access to database sessions,
Redis clients, and application settings.

Usage:
    @router.get("/items")
    async def list_items(
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
        settings: Settings = Depends(get_settings_dep),
    ):
        ...
"""

from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import AuthenticationException, NotFoundException
from app.db.redis import get_redis_client
from app.db.session import get_db_session
from app.models.user import User
from app.models.config import Organization
from app.repositories.user import UserRepository
from app.repositories.organization import (
    OrganizationRepository,
    OrganizationSettingsRepository,
    OrganizationMemberRepository,
    OrganizationInvitationRepository,
)
from app.repositories.rbac import (
    RoleRepository,
    PermissionRepository,
    UserRoleRepository,
    PermissionGroupRepository,
    RoleAuditLogRepository,
)
from app.repositories.billing import (
    PlanRepository,
    SubscriptionRepository,
    InvoiceRepository,
    PaymentRepository,
    PaymentMethodRepository,
    UsageRecordRepository,
    CouponRepository,
    DiscountRepository,
    TransactionRepository,
    RefundRepository,
)
from app.repositories.knowledge import (
    KnowledgeBaseRepository,
    KnowledgeCategoryRepository,
    DocumentRepository,
    DocumentVersionRepository,
    DocumentChunkRepository,
    EmbeddingJobRepository,
    TagRepository,
    CollectionRepository,
)
from app.repositories.ai_gateway import (
    AIProviderRepository,
    AIModelRepository,
    PromptTemplateRepository,
    PromptVersionRepository,
    AIRequestRepository,
    AIResponseRepository,
    ProviderHealthRepository,
)
from app.repositories.vector import (
    EmbeddingProviderRepository,
    EmbeddingModelRepository,
    VectorIndexRepository,
    SearchHistoryRepository,
    SearchFeedbackRepository,
)
from app.services.auth import AuthService
from app.services.organization import OrganizationService
from app.services.rbac import RBACService
from app.services.billing.billing import BillingService
from app.services.storage.provider import StorageProvider, LocalStorageProvider
from app.services.knowledge import KnowledgeService, DocumentService
from app.services.ai.gateway import AiGateway
from app.services.vector import VectorService
from app.utils.crypto import decode_jwt_token

reusable_oauth2 = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session.

    Wraps the session module's generator for use as a FastAPI dependency.

    Yields:
        AsyncSession: An async database session with automatic
                      commit/rollback handling.
    """
    async for session in get_db_session():
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Provide an async Redis client.

    Wraps the Redis module's generator for use as a FastAPI dependency.

    Yields:
        Redis: An async Redis client instance.
    """
    async for client in get_redis_client():
        yield client


def get_settings_dep() -> Settings:
    """
    Provide application settings.

    Returns the cached settings singleton for use as a FastAPI dependency.

    Returns:
        Settings: Application settings instance.
    """
    return get_settings()


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """
    Dependency that returns an instantiated UserRepository.
    """
    return UserRepository(session=db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    redis: Redis = Depends(get_redis),
    settings: Settings = Depends(get_settings_dep),
) -> AuthService:
    """
    Dependency that returns an instantiated AuthService.
    """
    return AuthService(user_repository=user_repo, redis_client=redis, settings=settings)


async def get_current_user(
    token_credentials: HTTPAuthorizationCredentials | None = Depends(reusable_oauth2),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Dependency that parses and verifies access tokens, resolving the active User object.
    """
    if not token_credentials:
        raise AuthenticationException(
            message="Not authenticated",
            error_code="NOT_AUTHENTICATED",
        )

    token = token_credentials.credentials
    # Decode access token
    payload = decode_jwt_token(token, expected_type="access")
    user_id = payload.get("sub")
    
    if not user_id:
        raise AuthenticationException(
            message="Invalid token structure",
            error_code="INVALID_TOKEN",
        )

    # Fetch user using a dummy/placeholder organization ID (ignores multi-tenant checks for core authentication)
    # We load user regardless of organization context for auth check
    user = await user_repo.get_by_email(payload.get("email", ""))
    
    if not user:
        raise AuthenticationException(
            message="User associated with token not found",
            error_code="USER_NOT_FOUND",
        )
        
    if not user.is_active:
        raise AuthenticationException(
            message="Account is deactivated",
            error_code="USER_DEACTIVATED",
        )

    return user


async def get_organization_repository(db: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    """
    Dependency that returns an instantiated OrganizationRepository.
    """
    return OrganizationRepository(session=db)


async def get_organization_settings_repository(db: AsyncSession = Depends(get_db)) -> OrganizationSettingsRepository:
    """
    Dependency that returns an instantiated OrganizationSettingsRepository.
    """
    return OrganizationSettingsRepository(session=db)


async def get_organization_member_repository(db: AsyncSession = Depends(get_db)) -> OrganizationMemberRepository:
    """
    Dependency that returns an instantiated OrganizationMemberRepository.
    """
    return OrganizationMemberRepository(session=db)


async def get_organization_invitation_repository(db: AsyncSession = Depends(get_db)) -> OrganizationInvitationRepository:
    """
    Dependency that returns an instantiated OrganizationInvitationRepository.
    """
    return OrganizationInvitationRepository(session=db)


async def get_organization_service(
    org_repo: OrganizationRepository = Depends(get_organization_repository),
    settings_repo: OrganizationSettingsRepository = Depends(get_organization_settings_repository),
    member_repo: OrganizationMemberRepository = Depends(get_organization_member_repository),
    invite_repo: OrganizationInvitationRepository = Depends(get_organization_invitation_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> OrganizationService:
    """
    Dependency that returns an instantiated OrganizationService.
    """
    return OrganizationService(
        org_repo=org_repo,
        settings_repo=settings_repo,
        member_repo=member_repo,
        invite_repo=invite_repo,
        user_repo=user_repo,
    )


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends(get_organization_service),
) -> Organization:
    """
    Security dependency that resolves the user's active tenant organization.
    Ensures the user belongs to the active organization session.
    """
    if not current_user.organization_id:
        raise AuthenticationException(
            message="User is not currently associated with any active organization workspace.",
            error_code="NO_ACTIVE_WORKSPACE",
        )

    # Fetch active organization context
    try:
        org = await org_service.get_organization(current_user.organization_id)
        
        # Verify user is a member of this active organization
        membership = await org_service.member_repo.get_member(org.id, current_user.id)
        if not membership:
            raise AuthenticationException(
                message="Access Denied: You are not a registered member of this organization workspace.",
                error_code="FORBIDDEN_WORKSPACE",
            )
            
        return org
    except NotFoundException:
        raise AuthenticationException(
            message="Active organization workspace not found or has been deactivated.",
            error_code="WORKSPACE_NOT_FOUND",
        )


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> RoleRepository:
    """
    Dependency that returns an instantiated RoleRepository.
    """
    return RoleRepository(session=db)


async def get_permission_repository(db: AsyncSession = Depends(get_db)) -> PermissionRepository:
    """
    Dependency that returns an instantiated PermissionRepository.
    """
    return PermissionRepository(session=db)


async def get_user_role_repository(db: AsyncSession = Depends(get_db)) -> UserRoleRepository:
    """
    Dependency that returns an instantiated UserRoleRepository.
    """
    return UserRoleRepository(session=db)


async def get_permission_group_repository(db: AsyncSession = Depends(get_db)) -> PermissionGroupRepository:
    """
    Dependency that returns an instantiated PermissionGroupRepository.
    """
    return PermissionGroupRepository(session=db)


async def get_role_audit_log_repository(db: AsyncSession = Depends(get_db)) -> RoleAuditLogRepository:
    """
    Dependency that returns an instantiated RoleAuditLogRepository.
    """
    return RoleAuditLogRepository(session=db)


async def get_rbac_service(
    role_repo: RoleRepository = Depends(get_role_repository),
    perm_repo: PermissionRepository = Depends(get_permission_repository),
    user_role_repo: UserRoleRepository = Depends(get_user_role_repository),
    group_repo: PermissionGroupRepository = Depends(get_permission_group_repository),
    audit_repo: RoleAuditLogRepository = Depends(get_role_audit_log_repository),
    org_repo: OrganizationRepository = Depends(get_organization_repository),
    redis: Redis = Depends(get_redis),
) -> RBACService:
    """
    Dependency that returns an instantiated RBACService.
    """
    return RBACService(
        role_repo=role_repo,
        perm_repo=perm_repo,
        user_role_repo=user_role_repo,
        group_repo=group_repo,
        audit_repo=audit_repo,
        org_repo=org_repo,
        redis=redis,
    )


async def get_plan_repository(db: AsyncSession = Depends(get_db)) -> PlanRepository:
    return PlanRepository(session=db)


async def get_subscription_repository(db: AsyncSession = Depends(get_db)) -> SubscriptionRepository:
    return SubscriptionRepository(session=db)


async def get_invoice_repository(db: AsyncSession = Depends(get_db)) -> InvoiceRepository:
    return InvoiceRepository(session=db)


async def get_payment_repository(db: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(session=db)


async def get_payment_method_repository(db: AsyncSession = Depends(get_db)) -> PaymentMethodRepository:
    return PaymentMethodRepository(session=db)


async def get_usage_record_repository(db: AsyncSession = Depends(get_db)) -> UsageRecordRepository:
    return UsageRecordRepository(session=db)


async def get_coupon_repository(db: AsyncSession = Depends(get_db)) -> CouponRepository:
    return CouponRepository(session=db)


async def get_discount_repository(db: AsyncSession = Depends(get_db)) -> DiscountRepository:
    return DiscountRepository(session=db)


async def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(session=db)


async def get_refund_repository(db: AsyncSession = Depends(get_db)) -> RefundRepository:
    return RefundRepository(session=db)


async def get_billing_service(
    plan_repo: PlanRepository = Depends(get_plan_repository),
    sub_repo: SubscriptionRepository = Depends(get_subscription_repository),
    invoice_repo: InvoiceRepository = Depends(get_invoice_repository),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    pm_repo: PaymentMethodRepository = Depends(get_payment_method_repository),
    usage_repo: UsageRecordRepository = Depends(get_usage_record_repository),
    coupon_repo: CouponRepository = Depends(get_coupon_repository),
    discount_repo: DiscountRepository = Depends(get_discount_repository),
    tx_repo: TransactionRepository = Depends(get_transaction_repository),
    refund_repo: RefundRepository = Depends(get_refund_repository),
    redis: Redis = Depends(get_redis),
) -> BillingService:
    return BillingService(
        plan_repo=plan_repo,
        sub_repo=sub_repo,
        invoice_repo=invoice_repo,
        payment_repo=payment_repo,
        pm_repo=pm_repo,
        usage_repo=usage_repo,
        coupon_repo=coupon_repo,
        discount_repo=discount_repo,
        tx_repo=tx_repo,
        refund_repo=refund_repo,
        redis=redis,
    )


async def get_knowledge_base_repository(db: AsyncSession = Depends(get_db)) -> KnowledgeBaseRepository:
    return KnowledgeBaseRepository(session=db)


async def get_knowledge_category_repository(db: AsyncSession = Depends(get_db)) -> KnowledgeCategoryRepository:
    return KnowledgeCategoryRepository(session=db)


async def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(session=db)


async def get_document_version_repository(db: AsyncSession = Depends(get_db)) -> DocumentVersionRepository:
    return DocumentVersionRepository(session=db)


async def get_document_chunk_repository(db: AsyncSession = Depends(get_db)) -> DocumentChunkRepository:
    return DocumentChunkRepository(session=db)


async def get_embedding_job_repository(db: AsyncSession = Depends(get_db)) -> EmbeddingJobRepository:
    return EmbeddingJobRepository(session=db)


async def get_tag_repository(db: AsyncSession = Depends(get_db)) -> TagRepository:
    return TagRepository(session=db)


async def get_collection_repository(db: AsyncSession = Depends(get_db)) -> CollectionRepository:
    return CollectionRepository(session=db)


async def get_storage_provider() -> StorageProvider:
    # Use LocalStorageProvider with default base path for development and tests
    return LocalStorageProvider()


async def get_knowledge_service(
    kb_repo: KnowledgeBaseRepository = Depends(get_knowledge_base_repository),
    cat_repo: KnowledgeCategoryRepository = Depends(get_knowledge_category_repository),
) -> KnowledgeService:
    return KnowledgeService(kb_repo=kb_repo, cat_repo=cat_repo)


async def get_document_service(
    doc_repo: DocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_document_version_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_document_chunk_repository),
    job_repo: EmbeddingJobRepository = Depends(get_embedding_job_repository),
    tag_repo: TagRepository = Depends(get_tag_repository),
    kb_repo: KnowledgeBaseRepository = Depends(get_knowledge_base_repository),
    storage: StorageProvider = Depends(get_storage_provider),
) -> DocumentService:
    return DocumentService(
        doc_repo=doc_repo,
        version_repo=version_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
        tag_repo=tag_repo,
        kb_repo=kb_repo,
        storage=storage,
    )


async def get_ai_provider_repository(db: AsyncSession = Depends(get_db)) -> AIProviderRepository:
    return AIProviderRepository(session=db)


async def get_ai_model_repository(db: AsyncSession = Depends(get_db)) -> AIModelRepository:
    return AIModelRepository(session=db)


async def get_prompt_template_repository(db: AsyncSession = Depends(get_db)) -> PromptTemplateRepository:
    return PromptTemplateRepository(session=db)


async def get_prompt_version_repository(db: AsyncSession = Depends(get_db)) -> PromptVersionRepository:
    return PromptVersionRepository(session=db)


async def get_ai_request_repository(db: AsyncSession = Depends(get_db)) -> AIRequestRepository:
    return AIRequestRepository(session=db)


async def get_ai_response_repository(db: AsyncSession = Depends(get_db)) -> AIResponseRepository:
    return AIResponseRepository(session=db)


async def get_provider_health_repository(db: AsyncSession = Depends(get_db)) -> ProviderHealthRepository:
    return ProviderHealthRepository(session=db)


async def get_ai_gateway(
    provider_repo: AIProviderRepository = Depends(get_ai_provider_repository),
    model_repo: AIModelRepository = Depends(get_ai_model_repository),
    template_repo: PromptTemplateRepository = Depends(get_prompt_template_repository),
    version_repo: PromptVersionRepository = Depends(get_prompt_version_repository),
    request_repo: AIRequestRepository = Depends(get_ai_request_repository),
    response_repo: AIResponseRepository = Depends(get_ai_response_repository),
    health_repo: ProviderHealthRepository = Depends(get_provider_health_repository),
) -> AiGateway:
    return AiGateway(
        provider_repo=provider_repo,
        model_repo=model_repo,
        template_repo=template_repo,
        version_repo=version_repo,
        request_repo=request_repo,
        response_repo=response_repo,
        health_repo=health_repo,
    )


async def get_embedding_provider_repository(db: AsyncSession = Depends(get_db)) -> EmbeddingProviderRepository:
    return EmbeddingProviderRepository(session=db)


async def get_embedding_model_repository(db: AsyncSession = Depends(get_db)) -> EmbeddingModelRepository:
    return EmbeddingModelRepository(session=db)


async def get_vector_index_repository(db: AsyncSession = Depends(get_db)) -> VectorIndexRepository:
    return VectorIndexRepository(session=db)


async def get_search_history_repository(db: AsyncSession = Depends(get_db)) -> SearchHistoryRepository:
    return SearchHistoryRepository(session=db)


async def get_search_feedback_repository(db: AsyncSession = Depends(get_db)) -> SearchFeedbackRepository:
    return SearchFeedbackRepository(session=db)


async def get_vector_service(
    provider_repo: EmbeddingProviderRepository = Depends(get_embedding_provider_repository),
    model_repo: EmbeddingModelRepository = Depends(get_embedding_model_repository),
    index_repo: VectorIndexRepository = Depends(get_vector_index_repository),
    history_repo: SearchHistoryRepository = Depends(get_search_history_repository),
    feedback_repo: SearchFeedbackRepository = Depends(get_search_feedback_repository),
) -> VectorService:
    return VectorService(
        provider_repo=provider_repo,
        model_repo=model_repo,
        index_repo=index_repo,
        history_repo=history_repo,
        feedback_repo=feedback_repo,
    )







