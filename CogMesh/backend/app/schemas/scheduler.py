"""Pydantic schemas for Scheduler API request validation."""

from pydantic import BaseModel, Field


class SchedulerPlanRequest(BaseModel):
    """Schema for scheduler execution plan generation request."""

    goal_id: str = Field(
        ...,
        min_length=1,
        description="Goal UUID for which to evaluate devices and generate an ExecutionPlan.",
        json_schema_extra={"example": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff"},
    )
