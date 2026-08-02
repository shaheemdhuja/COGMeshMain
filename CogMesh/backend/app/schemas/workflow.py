"""Pydantic schemas for Workflow API requests."""

from pydantic import BaseModel, Field


class WorkflowGenerateRequest(BaseModel):
    """Schema for workflow generation request payload."""

    goal_id: str = Field(
        ...,
        min_length=1,
        description="Goal UUID for which to generate the capability-constrained ExecutionDAG.",
        json_schema_extra={"example": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff"},
    )
