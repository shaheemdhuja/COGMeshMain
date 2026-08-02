"""Pydantic schemas for Goal Service API requests and responses."""

from pydantic import BaseModel, Field


class GoalParseRequest(BaseModel):
    """Schema for goal parsing request payload."""

    goal: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language request string submitted by user.",
        json_schema_extra={"example": "Summarize this lecture PDF and generate MCQs."},
    )
