"""
Nexora Platform — AI Agent Configurations ORM Models
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AiAgent(BaseModel):
    """
    AI Agents Table.
    Stores setup configuration parameters for customized AI employee instances.
    """

    __tablename__ = "ai_agents"

    knowledge_base_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_bases.id"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(nullable=False)
    model_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="openai")
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="gpt-4o")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    voice_stt_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    voice_tts_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    knowledge_base: Mapped[KnowledgeBase | None] = relationship("KnowledgeBase", back_populates="agents")
    tools: Mapped[list[AgentTool]] = relationship(
        "AgentTool",
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list[Conversation]] = relationship("Conversation", back_populates="agent")
    appointments: Mapped[list[Appointment]] = relationship("Appointment", back_populates="agent")

    def __repr__(self) -> str:
        return f"<AiAgent(id={self.id}, name={self.name}, org={self.organization_id})>"


class AgentTool(BaseModel):
    """
    Agent Tools Table.
    Binds concrete executable tools (visual n8n logic, custom logic integrations) to AI Agent definitions.
    """

    __tablename__ = "agent_tools"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_type: Mapped[str] = mapped_column(String(50), nullable=False)  # crm, calendar, email, n8n, etc.
    configuration: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    agent: Mapped[AiAgent] = relationship("AiAgent", back_populates="tools")

    def __repr__(self) -> str:
        return f"<AgentTool(id={self.id}, type={self.tool_type}, agent={self.agent_id})>"
