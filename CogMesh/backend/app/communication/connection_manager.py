"""ConnectionManager tracking active Runtime Node connections and session freshness in memory."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from loguru import logger

from app.communication.enums import ConnectionStatus
from app.communication.message import Connection


class ConnectionManager:
    """In-memory connection manager maintaining registered node connection sessions."""

    def __init__(self) -> None:
        """Initialize empty active connection mapping."""
        self._connections: Dict[str, Connection] = {}

    def register_connection(self, connection: Connection) -> Connection:
        """Register or update a node connection session."""
        connection.status = ConnectionStatus.CONNECTED
        connection.last_seen = datetime.now(timezone.utc)
        self._connections[connection.node_id] = connection
        logger.info(
            f"[ConnectionManager] Registered connection '{connection.connection_id}' for node '{connection.node_id}'"
        )
        return connection

    def remove_connection(self, node_id: str) -> Optional[Connection]:
        """Disconnect and remove node connection."""
        conn = self._connections.pop(node_id, None)
        if conn:
            conn.status = ConnectionStatus.DISCONNECTED
            logger.info(f"[ConnectionManager] Removed connection for node '{node_id}'")
        return conn

    def get_connection(self, node_id: str) -> Optional[Connection]:
        """Retrieve connection session by node_id."""
        return self._connections.get(node_id)

    def get_all_connections(self) -> List[Connection]:
        """Retrieve list of all active or managed connections."""
        return list(self._connections.values())

    def update_last_seen(self, node_id: str) -> Optional[Connection]:
        """Refresh last_seen timestamp for a connected node."""
        conn = self._connections.get(node_id)
        if conn:
            conn.last_seen = datetime.now(timezone.utc)
            if conn.status == ConnectionStatus.STALE:
                conn.status = ConnectionStatus.CONNECTED
        return conn

    def clear(self) -> None:
        """Purge all active connections."""
        self._connections.clear()
