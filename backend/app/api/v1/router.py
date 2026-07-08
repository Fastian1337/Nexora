"""
Nexora Platform — API v1 Router

Aggregates all v1 endpoint routers into a single router.
New modules should register their routers here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.organizations import router as organizations_router
from app.api.v1.endpoints.rbac import router as rbac_router
from app.api.v1.endpoints.billing import router as billing_router
from app.api.v1.endpoints.knowledge import router as knowledge_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.vector import router as vector_router

router = APIRouter()

# Register endpoint routers
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(organizations_router)
router.include_router(rbac_router)
router.include_router(billing_router)
router.include_router(knowledge_router)
router.include_router(ai_router)
router.include_router(vector_router)

