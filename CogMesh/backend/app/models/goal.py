"""Goal ORM Model representing user natural language requests."""

from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.workflow import Workflow
    from app.models.result import Result


class Goal(Base, UUIDMixin, TimestampMixin):
    """Represents a submitted natural language goal and its decomposition state."""

    __tablename__ = "goals"

    natural_language_input: Mapped[str] = mapped_column(Text, nullable=False)
    structured_goal: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)

    # Relationships
    workflows: Mapped[List["Workflow"]] = relationship("Workflow", back_populates="goal", cascade="all, delete-orphan")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="goal", cascade="all, delete-orphan")
