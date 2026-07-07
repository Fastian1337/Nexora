"""
Nexora Platform — Third Party Integrations & Webhooks ORM Models
"""

from __future__ import annotations

from sqlalchemy import Boolean, LargeBinary, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Integration(BaseModel):
    """
    Integrations Table.
    Stores encrypted keys and credentials to connect third-party platforms (CRM, Calendar, WhatsApp).
    """

    __tablename__ = "integrations"

    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    credentials: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Encrypted credentials payload
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, provider={self.provider}, active={self.is_active})>"


class Webhook(BaseModel):
    """
    Webhooks Table.
    Registers target webhook URLs for outgoing event notifications.
    """

    __tablename__ = "webhooks"

    target_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    event_types: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False)
    secret_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, target={self.target_url}, active={self.is_active})>"
