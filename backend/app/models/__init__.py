"""
Nexora Platform — ORM Models Registry

All SQLAlchemy models are imported here so that:
1. They are registered on the Base.metadata object.
2. Alembic's env.py can discover all models for autogenerate.
3. They are easily importable from a single package index.
"""

from __future__ import annotations

# Base Models
from app.models.base import Base, BaseModel

# System & Config Models
from app.models.config import Organization, File, SystemSettings

# User & Access Models
from app.models.user import Permission, Role, User, role_permissions, user_roles

# Billing Models
from app.models.billing import Plan, Subscription

# Knowledge Base Models
from app.models.knowledge import KnowledgeBase, Document, Embedding

# Agent Models
from app.models.agent import AiAgent, AgentTool

# Communication Models
from app.models.communication import Conversation, Message, VoiceCall, Appointment

# Automation Models
from app.models.automation import WorkflowExecution, AutomationLog

# Marketing Models
from app.models.marketing import MarketingCampaign, SocialPost, ContentLibrary

# Observability Models
from app.models.observability import AuditLog, Notification, Analytics

# Integration Models
from app.models.integration import Integration, Webhook

__all__ = [
    "Base",
    "BaseModel",
    "Organization",
    "File",
    "SystemSettings",
    "Permission",
    "Role",
    "User",
    "role_permissions",
    "user_roles",
    "Plan",
    "Subscription",
    "KnowledgeBase",
    "Document",
    "Embedding",
    "AiAgent",
    "AgentTool",
    "Conversation",
    "Message",
    "VoiceCall",
    "Appointment",
    "WorkflowExecution",
    "AutomationLog",
    "MarketingCampaign",
    "SocialPost",
    "ContentLibrary",
    "AuditLog",
    "Notification",
    "Analytics",
    "Integration",
    "Webhook",
]
