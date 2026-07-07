"""
Nexora Platform — Conversations & Telephony Communications ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Conversation(BaseModel):
    """
    Conversations Table.
    Groups message history threads per agent-user interaction channel.
    """

    __tablename__ = "conversations"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_agents.id"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # whatsapp, web, voice, etc.
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    external_contact_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    agent: Mapped[AiAgent] = relationship("AiAgent", back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    voice_calls: Mapped[list[VoiceCall]] = relationship(
        "VoiceCall",
        back_populates="conversation",
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, agent={self.agent_id}, channel={self.channel})>"


class Message(BaseModel):
    """
    Messages Table.
    Individual conversation turns sent/received via communication streams.
    """

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, name="metadata", nullable=True, default=dict)

    # Relationships
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation={self.conversation_id}, role={self.role})>"


class VoiceCall(BaseModel):
    """
    Voice Calls Table.
    Logs parameters of VoIP/Telephony connections handled by AI Speech systems.
    """

    __tablename__ = "voice_calls"

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=True,
        index=True,
    )
    telephony_provider: Mapped[str] = mapped_column(String(50), nullable=False)  # twilio, etc.
    call_sid: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # inbound, outbound
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")

    # Relationships
    conversation: Mapped[Conversation | None] = relationship("Conversation", back_populates="voice_calls")

    def __repr__(self) -> str:
        return f"<VoiceCall(id={self.id}, call_sid={self.call_sid})>"


class Appointment(BaseModel):
    """
    Appointments Table.
    Schedules booked bookings/meetings orchestrated by front-office receptionist modules.
    """

    __tablename__ = "appointments"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_agents.id"),
        nullable=False,
        index=True,
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled", index=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)

    # Relationships
    agent: Mapped[AiAgent] = relationship("AiAgent", back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, start={self.start_time}, status={self.status})>"
