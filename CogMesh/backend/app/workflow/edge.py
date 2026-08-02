"""ExecutionEdge model representing dependency links between ExecutionNodes."""

import uuid
from pydantic import BaseModel, Field


class ExecutionEdge(BaseModel):
    """Represents a directed dependency edge from source node to destination node."""

    edge_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the dependency edge.",
    )
    source: str = Field(
        ...,
        description="node_id of precursor source node.",
    )
    destination: str = Field(
        ...,
        description="node_id of successor destination node.",
    )
