"""TaskResult model encapsulating AI task adapter execution outputs and telemetry."""

import uuid
from typing import Any, Dict
from pydantic import BaseModel, Field

from app.tasks.enums import TaskStatus


class TaskResult(BaseModel):
    """Encapsulates output artifact data and performance metrics returned by a task adapter."""

    task_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the task execution result.",
    )
    status: TaskStatus = Field(
        default=TaskStatus.SUCCESS,
        description="Execution status of the task adapter run.",
    )
    output: Dict[str, Any] = Field(
        default_factory=dict,
        description="Artifact output dictionary produced by the AI model/adapter.",
    )
    execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Execution latency in milliseconds.",
    )
    adapter_name: str = Field(
        ...,
        description="Name of the executing TaskAdapter subclass.",
    )
    provider_name: str = Field(
        ...,
        description="Name of the underlying AI model provider (e.g. MockOCRProvider, MockGemmaProvider).",
    )
    model_name: str = Field(
        ...,
        description="Name of the underlying AI model (e.g. mock-tesseract-v5, mock-gemma-2b).",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata and telemetry parameters.",
    )
