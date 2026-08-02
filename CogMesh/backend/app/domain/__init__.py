"""Domain models package containing runtime domain objects independent of ORM models."""

from app.domain.structured_goal import StructuredGoal
from app.domain.execution_context import ExecutionContext

__all__ = ["StructuredGoal", "ExecutionContext"]
