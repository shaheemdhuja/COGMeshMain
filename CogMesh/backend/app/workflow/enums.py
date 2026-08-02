"""Enumerations used across the Workflow DAG subsystem."""

from enum import Enum


class TaskType(str, Enum):
    """Supported task operation types."""

    OCR = "OCR"
    SUMMARIZATION = "SUMMARIZATION"
    TRANSLATION = "TRANSLATION"
    MCQ_GENERATION = "MCQ_GENERATION"
    UNKNOWN = "UNKNOWN"


class NodeStatus(str, Enum):
    """Lifecycle state machine status for an individual DAG node."""

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStatus(str, Enum):
    """Overall status of an execution DAG workflow."""

    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    OPTIMIZED = "OPTIMIZED"
    FAILED = "FAILED"
