"""Pydantic schemas for health check and status endpoints."""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema representing the health status response of the runtime backend."""

    status: str = Field(..., example="healthy")
    project_name: str = Field(..., example="CogMesh Runtime Engine")
    database_connected: bool = Field(..., example=True)
    timestamp: datetime = Field(..., example="2026-08-02T13:00:00Z")
