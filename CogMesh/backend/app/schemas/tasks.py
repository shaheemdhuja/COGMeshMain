"""Pydantic schemas for AI Task Adapter API requests and responses."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class TaskExecuteRequest(BaseModel):
    """Schema for dispatching execution of a task through the AI task adapter layer."""

    task_type: str = Field(
        ...,
        min_length=1,
        description="Type of AI task operation (e.g. OCR, SUMMARIZATION, TRANSLATION, MCQ_GENERATION).",
        json_schema_extra={"example": "OCR"},
    )
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters and artifact metadata passed to the adapter.",
        json_schema_extra={"example": {"page": 1, "language": "English"}},
    )


class TaskAdapterResponse(BaseModel):
    """Schema describing registered AI task adapter capability metadata."""

    task_type: str = Field(..., description="Registered task type key.")
    adapter_name: str = Field(..., description="Class name of the task adapter.")
    provider_name: str = Field(..., description="Provider name of the AI model engine.")
    model_name: str = Field(..., description="Model name of the underlying AI engine.")
    supported_capabilities: List[str] = Field(..., description="List of supported task capabilities.")
