"""
Nexora Platform — Visual Workflows & Connector Logs ORM Models
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class WorkflowExecution(BaseModel):
    """
    Workflow Executions Table.
    Tracks triggers sent to the execution engine (n8n).
    """

    __tablename__ = "workflow_executions"

    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running", index=True)
    execution_id: Mapped[str] = mapped_column(String(255), nullable=False)  # n8n execution id
    trigger_source: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    logs: Mapped[list[AutomationLog]] = relationship(
        "AutomationLog",
        back_populates="execution",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, workflow={self.workflow_name}, status={self.status})>"


class AutomationLog(BaseModel):
    """
    Automation Logs Table.
    Stores fine-grained execution steps, parameters, and payloads within triggered workflows.
    """

    __tablename__ = "automation_logs"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)

    # Relationships
    execution: Mapped[WorkflowExecution] = relationship("WorkflowExecution", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AutomationLog(id={self.id}, execution={self.execution_id}, step={self.step_name})>"
