"""Domain models for RuntimeMessage and Connection representation."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field

from app.communication.enums import ConnectionStatus, MessageType, TransportType


class RuntimeMessage(BaseModel):
    """Protocol message object transmitted across the CogMesh communication layer."""

    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the runtime message.",
    )
    message_type: MessageType = Field(
        ...,
        description="Type of protocol message (e.g. TASK_ASSIGNMENT, RESULT, HEARTBEAT).",
    )
    source_node: str = Field(
        ...,
        description="Node ID originating the message (or 'ORCHESTRATOR').",
    )
    destination_node: str = Field(
        ...,
        description="Target Node ID intended to receive the message (or 'BROADCAST').",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when message was instantiated.",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary JSON payload containing task arguments or results.",
    )


class Connection(BaseModel):
    """Representation of an active or managed node connection."""

    connection_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the connection session.",
    )
    node_id: str = Field(
        ...,
        description="Edge device ID or Runtime Node ID associated with the connection.",
    )
    status: ConnectionStatus = Field(
        default=ConnectionStatus.CONNECTED,
        description="Current status of the connection (CONNECTED, DISCONNECTED, STALE).",
    )
    last_seen: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last received heartbeat or message.",
    )
    transport: TransportType = Field(
        default=TransportType.WEBSOCKET,
        description="Transport technology used for this connection.",
    )
