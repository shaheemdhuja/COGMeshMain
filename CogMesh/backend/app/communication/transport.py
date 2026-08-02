"""Abstract base Transport interface defining transport-independent messaging contracts."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.communication.message import Connection, RuntimeMessage


class Transport(ABC):
    """Abstract interface for node messaging transport implementations (WebSocket, gRPC, Mock)."""

    @abstractmethod
    async def connect(self, node_id: str, socket: Any = None) -> Connection:
        """Establish connection session for a node."""
        pass

    @abstractmethod
    async def disconnect(self, node_id: str) -> None:
        """Terminate connection session for a node."""
        pass

    @abstractmethod
    async def send(self, message: RuntimeMessage) -> bool:
        """Send a RuntimeMessage to its destination node."""
        pass

    @abstractmethod
    async def broadcast(self, message: RuntimeMessage) -> int:
        """Broadcast a RuntimeMessage to all connected nodes."""
        pass

    @abstractmethod
    async def receive(self, node_id: str) -> Optional[RuntimeMessage]:
        """Receive next pending RuntimeMessage for a node, if available."""
        pass
