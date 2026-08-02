"""Pydantic schemas for Runtime Orchestrator API request validation."""

from pydantic import BaseModel, Field


class RuntimeStartRequest(BaseModel):
    """Schema for requesting execution start of a goal's ExecutionPlan."""

    goal_id: str = Field(
        ...,
        min_length=1,
        description="Goal UUID for which to execute the scheduled ExecutionPlan.",
        json_schema_extra={"example": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"},
    )
