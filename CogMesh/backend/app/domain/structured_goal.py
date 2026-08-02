"""Domain object representing a structured internal goal decoupled from natural language."""

import uuid
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class StructuredGoal(BaseModel):
    """Structured internal representation of a user goal after natural language parsing."""

    goal_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the parsed goal.",
    )
    natural_language_input: str = Field(
        ...,
        description="Original raw natural language input string.",
    )
    goal_type: str = Field(
        default="general_pipeline",
        description="High-level category of the requested workflow (e.g., 'lecture_processing').",
    )
    input_type: str = Field(
        default="unknown",
        description="Type of source input asset (e.g., 'pdf', 'text', 'image').",
    )
    operations: List[str] = Field(
        ...,
        min_length=1,
        description="Ordered sequence of atomic AI operations to execute.",
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Priority level: 1 (Normal), 2 (High), 3 (Critical).",
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional execution constraints (e.g., target language, max latency).",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parsing metadata, timestamps, and parser version details.",
    )
