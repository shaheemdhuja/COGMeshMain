"""Enumerations for Runtime Orchestrator state machines and events."""

from enum import Enum


class TaskState(str, Enum):
    """Task node execution lifecycle states."""

    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RuntimeEventType(str, Enum):
    """Runtime orchestration lifecycle event types."""

    PLAN_STARTED = "PLAN_STARTED"
    PLAN_COMPLETED = "PLAN_COMPLETED"
    TASK_READY = "TASK_READY"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    TASK_CANCELLED = "TASK_CANCELLED"


class RuntimeStatus(str, Enum):
    """Overall execution context status."""

    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
