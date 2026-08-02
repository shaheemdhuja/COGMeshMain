"""Pydantic schemas for Device management API request validation and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_serializer


class DeviceCreate(BaseModel):
    """Schema for registering a new edge device."""

    device_id: Optional[UUID] = Field(
        default=None,
        description="Optional client-provided unique device UUID. Auto-generated if omitted.",
    )
    device_name: str = Field(..., min_length=1, max_length=255, example="Master Laptop")
    device_type: str = Field(..., min_length=1, max_length=50, example="LAPTOP")
    ip_address: IPvAnyAddress = Field(..., example="192.168.1.50")
    port: int = Field(default=8000, ge=1, le=65535, example=8000)
    platform: str = Field(default="unknown", max_length=50, example="windows")

    @field_serializer("ip_address")
    def serialize_ip(self, ip: IPvAnyAddress) -> str:
        """Serialize IPvAnyAddress object to string."""
        return str(ip)


class HeartbeatRequest(BaseModel):
    """Schema for incoming device heartbeat telemetry."""

    device_id: UUID = Field(..., description="Unique device UUID sending heartbeat.")
    status: str = Field(default="ONLINE", max_length=50, example="ONLINE")


class DeviceResponse(BaseModel):
    """Schema representing device state returned to API clients."""

    model_config = ConfigDict(from_attributes=True)

    device_id: str = Field(..., validation_alias="id")
    device_name: str
    device_type: str
    ip_address: str
    port: int
    platform: str
    status: str
    registered_at: datetime = Field(..., validation_alias="created_at")
    last_seen: datetime

