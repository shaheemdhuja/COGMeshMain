"""ExecutionMetric ORM Model representing performance and resource utilization metrics."""

from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.task import Task


class ExecutionMetric(Base, UUIDMixin, TimestampMixin):
    """Represents performance and power metrics recorded for a completed task."""

    __tablename__ = "execution_metrics"

    goal_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ram_usage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    power_consumed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="metrics")
