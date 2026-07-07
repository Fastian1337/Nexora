"""
Nexora Platform — Observability, Analytics & Messaging ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AuditLog(BaseModel):
    """
    Audit Logs Table.
    System ledger capturing tenant mutations, details of deleted items, and API changes.
    """

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    old_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, target={self.target_type})>"


class Notification(BaseModel):
    """
    Notifications Table.
    System outbox tracking outbound emails, SMS alerts, and campaign updates sent to users.
    """

    __tablename__ = "notifications"

    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # email, sms, whatsapp
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, channel={self.channel}, status={self.status})>"


class Analytics(BaseModel):
    """
    Analytics Table.
    Timeseries rolled metrics used to compute platform usage logs and billing constraints.
    """

    __tablename__ = "analytics"

    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Analytics(id={self.id}, metric={self.metric_name}, val={self.value})>"
