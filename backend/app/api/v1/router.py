"""
Nexora Platform — API v1 Router

Aggregates all v1 endpoint routers into a single router.
New modules should register their routers here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router

router = APIRouter()

# Register endpoint routers
router.include_router(health_router)
router.include_router(auth_router)

