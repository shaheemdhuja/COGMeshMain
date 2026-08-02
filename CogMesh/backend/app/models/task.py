"""Task ORM Model representing an individual node execution unit in a workflow DAG."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.metric import ExecutionMetric
    from app.models.result import Result
    from app.models.task_log import TaskLog
    from app.models.workflow import Workflow


class Task(Base, UUIDMixin, TimestampMixin):
    """Represents a scheduled task within a Workflow DAG."""

    __tablename__ = "tasks"

    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., PDF_PARSE, OCR, SUMMARIZE, TRANSLATE
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)  # PENDING, DISPATCHED, RUNNING, COMPLETED, FAILED
    assigned_device_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="tasks")
    assigned_device: Mapped[Optional["Device"]] = relationship("Device", back_populates="assigned_tasks")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="task", cascade="all, delete-orphan")
    task_logs: Mapped[List["TaskLog"]] = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")
    metrics: Mapped[List["ExecutionMetric"]] = relationship("ExecutionMetric", back_populates="task", cascade="all, delete-orphan")
