"""RuntimeEvent model capturing orchestration lifecycle events and audit telemetry."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.runtime.enums import RuntimeEventType


class RuntimeEvent(BaseModel):
    """Event emitted during ExecutionPlan orchestration."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the runtime event.",
    )
    event_type: RuntimeEventType = Field(
        ...,
        description="Category of runtime event (e.g. TASK_STARTED, TASK_COMPLETED).",
    )
    context_id: str = Field(
        ...,
        description="ExecutionContext UUID associated with this event.",
    )
    goal_id: str = Field(
        ...,
        description="Goal UUID associated with this event.",
    )
    node_id: Optional[str] = Field(
        default=None,
        description="ExecutionNode ID associated with task-level events.",
    )
    device_id: Optional[str] = Field(
        default=None,
        description="Edge device ID assigned to the task.",
    )
    message: str = Field(
        ...,
        description="Human-readable event description.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when event was emitted.",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata and execution metrics.",
    )
