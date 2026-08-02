"""TaskAssignment model representing the mapping of an ExecutionNode to a target edge Device."""

import uuid
from pydantic import BaseModel, Field

from app.workflow.enums import TaskType


class TaskAssignment(BaseModel):
    """Represents a scheduled binding between a DAG task node and an assigned edge device."""

    assignment_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the task assignment binding.",
    )
    node_id: str = Field(
        ...,
        description="node_id of the assigned ExecutionNode from the ExecutionDAG.",
    )
    device_id: str = Field(
        ...,
        description="device_id of the assigned edge device.",
    )
    task_type: TaskType = Field(
        ...,
        description="Type of task operation (e.g. OCR, SUMMARIZATION).",
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Task priority level (1=Normal, 2=High, 3=Critical).",
    )
    reason: str = Field(
        ...,
        description="Human-readable justification for device selection (e.g. scoring factors).",
    )
    estimated_duration: float = Field(
        default=1.0,
        ge=0.0,
        description="Estimated execution time in seconds.",
    )
