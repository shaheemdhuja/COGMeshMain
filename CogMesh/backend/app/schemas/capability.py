"""Pydantic v2 schemas for Capability Registry reporting, updates, and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CapabilityReport(BaseModel):
    """Schema for submitting or reporting a device capability snapshot."""

    device_id: UUID = Field(..., description="UUID of the device reporting capabilities.")
    cpu_cores: int = Field(..., gt=0, description="Total number of physical/logical CPU cores.", json_schema_extra={"example": 8})
    ram_gb: float = Field(..., gt=0.0, description="Total system RAM in Gigabytes.", json_schema_extra={"example": 16.0})
    battery_level: float = Field(..., ge=0.0, le=100.0, description="Battery percentage (0.0 - 100.0).", json_schema_extra={"example": 85.5})
    network_quality: str = Field(default="GOOD", max_length=50, description="Network quality status.", json_schema_extra={"example": "EXCELLENT"})
    supported_tasks: List[str] = Field(..., min_length=1, description="List of task types supported by the node.", json_schema_extra={"example": ["OCR", "SUMMARIZATION", "TRANSLATION"]})


class CapabilityUpdate(BaseModel):
    """Schema for partial update of device capability details."""

    cpu_cores: Optional[int] = Field(default=None, gt=0)
    ram_gb: Optional[float] = Field(default=None, gt=0.0)
    battery_level: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    network_quality: Optional[str] = Field(default=None, max_length=50)
    supported_tasks: Optional[List[str]] = Field(default=None, min_length=1)


class CapabilityResponse(BaseModel):
    """Schema representing capability record returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    cpu_cores: int
    ram_gb: float
    battery_level: float
    network_quality: str
    supported_tasks: List[str]
    last_updated: datetime
