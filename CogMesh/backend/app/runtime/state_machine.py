"""TaskStateMachine managing valid state transitions for task node execution lifecycles."""

from typing import Dict, Set
from app.core.exceptions import WorkflowException
from app.runtime.enums import TaskState


class TaskStateMachine:
    """State machine enforcing strict lifecycle transition rules for DAG task nodes."""

    VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
        TaskState.PENDING: {TaskState.READY, TaskState.CANCELLED},
        TaskState.READY: {TaskState.RUNNING, TaskState.CANCELLED},
        TaskState.RUNNING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.COMPLETED: set(),  # Terminal state
        TaskState.FAILED: set(),     # Terminal state
        TaskState.CANCELLED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(cls, current_state: TaskState, next_state: TaskState) -> bool:
        """Check if transition from current_state to next_state is valid."""
        allowed = cls.VALID_TRANSITIONS.get(current_state, set())
        return next_state in allowed

    @classmethod
    def transition(cls, current_state: TaskState, next_state: TaskState) -> TaskState:
        """Execute state transition if valid, or raise WorkflowException if forbidden."""
        if not cls.can_transition(current_state, next_state):
            raise WorkflowException(
                f"Invalid task state transition: cannot transition from '{current_state.value}' to '{next_state.value}'."
            )
        return next_state
