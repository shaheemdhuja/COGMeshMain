"""Workflow ORM Model representing execution DAGs generated from goals."""

from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.task import Task


class Workflow(Base, UUIDMixin, TimestampMixin):
    """Represents a generated and scheduled execution DAG for a specific goal."""

    __tablename__ = "workflows"

    goal_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    dag_structure: Mapped[dict] = mapped_column(JSON, nullable=False)  # DAG node graph structure and dependencies
    status: Mapped[str] = mapped_column(String(50), default="CREATED", index=True, nullable=False)  # CREATED, RUNNING, COMPLETED, FAILED

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="workflows")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="workflow", cascade="all, delete-orphan")
