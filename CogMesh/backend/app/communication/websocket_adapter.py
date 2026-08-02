"""WebSocketAdapter implementing abstract Transport interface over WebSocket connections."""

from collections import deque
from typing import Any, Dict, List, Optional
from loguru import logger

from app.communication.connection_manager import ConnectionManager
from app.communication.enums import TransportType
from app.communication.message import Connection, RuntimeMessage
from app.communication.protocol import serialize_message
from app.communication.transport import Transport


class WebSocketAdapter(Transport):
    """WebSocket implementation of Transport interface maintaining socket references and message queues."""

    def __init__(self, connection_manager: Optional[ConnectionManager] = None) -> None:
        """Initialize adapter with ConnectionManager and in-memory socket and message queues."""
        self.manager = connection_manager or ConnectionManager()
        self._sockets: Dict[str, Any] = {}
        self._inbound_queues: Dict[str, deque[RuntimeMessage]] = {}
        self._message_history: List[RuntimeMessage] = []

    async def connect(self, node_id: str, socket: Any = None) -> Connection:
        """Connect node, store socket reference, and register connection session."""
        connection = Connection(
            node_id=node_id,
            transport=TransportType.WEBSOCKET,
        )
        self.manager.register_connection(connection)
        if socket is not None:
            self._sockets[node_id] = socket
        if node_id not in self._inbound_queues:
            self._inbound_queues[node_id] = deque()

        logger.info(f"[WebSocketAdapter] Node '{node_id}' connected via WebSocket adapter.")
        return connection

    async def disconnect(self, node_id: str) -> None:
        """Disconnect node and cleanup socket reference."""
        self._sockets.pop(node_id, None)
        self._inbound_queues.pop(node_id, None)
        self.manager.remove_connection(node_id)
        logger.info(f"[WebSocketAdapter] Node '{node_id}' disconnected from WebSocket adapter.")

    async def send(self, message: RuntimeMessage) -> bool:
        """Send a RuntimeMessage to its destination node."""
        self._message_history.append(message)
        dest = message.destination_node

        conn = self.manager.get_connection(dest)
        if not conn:
            logger.warning(f"[WebSocketAdapter] Cannot send message to '{dest}': node not connected.")
            return False

        self.manager.update_last_seen(dest)

        # Enqueue in recipient's inbound queue
        if dest not in self._inbound_queues:
            self._inbound_queues[dest] = deque()
        self._inbound_queues[dest].append(message)

        # If underlying socket object exists and has send_text / send_json
        socket = self._sockets.get(dest)
        if socket:
            try:
                raw_payload = serialize_message(message)
                if hasattr(socket, "send_text"):
                    await socket.send_text(raw_payload)
                elif hasattr(socket, "send"):
                    await socket.send(raw_payload)
            except Exception as e:
                logger.error(f"[WebSocketAdapter] Error sending frame to socket for node '{dest}': {e}")
                return False

        logger.info(f"[WebSocketAdapter] Sent message '{message.message_type.value}' to '{dest}'")
        return True

    async def broadcast(self, message: RuntimeMessage) -> int:
        """Broadcast RuntimeMessage to all connected nodes."""
        connections = self.manager.get_all_connections()
        delivered_count = 0

        for conn in connections:
            single_msg = message.model_copy()
            single_msg.destination_node = conn.node_id
            if await self.send(single_msg):
                delivered_count += 1

        logger.info(f"[WebSocketAdapter] Broadcast message '{message.message_type.value}' to {delivered_count} nodes.")
        return delivered_count

    async def receive(self, node_id: str) -> Optional[RuntimeMessage]:
        """Pop next pending RuntimeMessage from node's inbound queue."""
        queue = self._inbound_queues.get(node_id)
        if not queue or len(queue) == 0:
            return None
        return queue.popleft()

    def get_message_history(self) -> List[RuntimeMessage]:
        """Retrieve recent transmitted RuntimeMessages."""
        return list(self._message_history)
