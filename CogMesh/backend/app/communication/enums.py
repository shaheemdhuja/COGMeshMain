"""Enumerations for Mesh Communication Layer message protocol and transports."""

from enum import Enum


class MessageType(str, Enum):
    """Protocol message types for node-to-node and orchestrator communications."""

    REGISTER = "REGISTER"
    REGISTER_ACK = "REGISTER_ACK"
    HEARTBEAT = "HEARTBEAT"
    PING = "PING"
    PONG = "PONG"
    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    TASK_RESULT = "TASK_RESULT"
    RESULT = "RESULT"
    ERROR = "ERROR"



class ConnectionStatus(str, Enum):
    """Lifecycle status of a Runtime Node connection."""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    STALE = "STALE"
    RECONNECTING = "RECONNECTING"


class TransportType(str, Enum):
    """Supported transport adapter technologies."""

    WEBSOCKET = "WEBSOCKET"
    HTTP_POLLING = "HTTP_POLLING"
    MOCK_INMEMORY = "MOCK_INMEMORY"
