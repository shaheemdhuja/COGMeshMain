"""Protocol helper utilities for RuntimeMessage construction, serialization, and parsing."""

import json
from typing import Any, Dict
from pydantic import ValidationError

from app.communication.enums import MessageType
from app.communication.message import RuntimeMessage
from app.core.exceptions import CogMeshException


class ProtocolException(CogMeshException):
    """Raised when message protocol parsing or serialization fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


def create_message(
    message_type: MessageType,
    source_node: str,
    destination_node: str,
    payload: Dict[str, Any] = None,
) -> RuntimeMessage:
    """Construct a validated RuntimeMessage instance."""
    return RuntimeMessage(
        message_type=message_type,
        source_node=source_node,
        destination_node=destination_node,
        payload=payload or {},
    )


def serialize_message(message: RuntimeMessage) -> str:
    """Serialize RuntimeMessage model to JSON string."""
    return message.model_dump_json()


def deserialize_message(raw_data: str) -> RuntimeMessage:
    """Parse raw JSON string into a validated RuntimeMessage instance."""
    try:
        data = json.loads(raw_data)
        return RuntimeMessage(**data)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        raise ProtocolException(f"Invalid RuntimeMessage format: {str(e)}")


parse_message = deserialize_message

