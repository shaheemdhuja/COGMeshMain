"""ExecutionNode model representing an atomic operation node in a workflow DAG."""

import uuid
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.workflow.enums import NodeStatus, TaskType


class ExecutionNode(BaseModel):
    """Represents a single task node within an ExecutionDAG."""

    node_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the execution DAG node.",
    )
    task_type: TaskType = Field(
        ...,
        description="Type of task operation to execute (e.g. OCR, SUMMARIZATION).",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of precursor node_ids that must complete before this node can run.",
    )
    required_capabilities: List[str] = Field(
        default_factory=list,
        description="Hardware/AI capabilities required by this node (e.g. ['OCR']).",
    )
    status: NodeStatus = Field(
        default=NodeStatus.PENDING,
        description="Current execution state of the node.",
    )
    estimated_cost: float = Field(
        default=1.0,
        ge=0.0,
        description="Estimated compute/memory complexity cost multiplier.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Task-specific parameters and metadata.",
    )
