"""Domain object representing the in-memory runtime execution context for a goal workflow."""

import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.domain.structured_goal import StructuredGoal


class ExecutionContext(BaseModel):
    """Central runtime object tracking the in-memory state of an active collaborative AI workflow."""

    context_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the runtime execution context.",
    )
    goal_id: str = Field(
        ...,
        description="ID of the goal associated with this execution context.",
    )
    goal: Optional[StructuredGoal] = Field(
        default=None,
        description="The structured goal definition being executed.",
    )
    workflow: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Generated execution DAG structure and node dependencies.",
    )
    devices: Dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of participating edge node devices (device_id -> metadata).",
    )
    capabilities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of participating device capabilities (device_id -> capability).",
    )
    task_states: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic state machine tracking active task statuses (task_id -> status).",
    )
    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Intermediate and final task execution results (task_id -> payload).",
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime execution performance metrics (task_id -> metric telemetry).",
    )
