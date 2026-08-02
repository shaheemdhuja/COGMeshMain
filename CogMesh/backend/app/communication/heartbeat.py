"""CommunicationHeartbeatService monitoring connection freshness and detecting stale sessions."""

from datetime import datetime, timezone
from typing import List
from loguru import logger

from app.communication.connection_manager import ConnectionManager
from app.communication.enums import ConnectionStatus


class CommunicationHeartbeatService:
    """Service detecting stale node connections based on configurable heartbeat thresholds."""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        """Initialize service with reference to ConnectionManager."""
        self.manager = connection_manager

    def check_stale_connections(self, timeout_seconds: float = 30.0) -> List[str]:
        """Scan active connections and mark nodes whose last_seen exceeds timeout_seconds as STALE."""
        now = datetime.now(timezone.utc)
        stale_nodes: List[str] = []

        for conn in self.manager.get_all_connections():
            elapsed = (now - conn.last_seen).total_seconds()
            if elapsed > timeout_seconds and conn.status == ConnectionStatus.CONNECTED:
                conn.status = ConnectionStatus.STALE
                stale_nodes.append(conn.node_id)
                logger.warning(
                    f"[HeartbeatService] Connection for node '{conn.node_id}' is STALE "
                    f"(no heartbeat for {elapsed:.1f}s)."
                )

        return stale_nodes

    def process_heartbeat(self, node_id: str) -> bool:
        """Process incoming heartbeat for a node, updating last_seen timestamp."""
        conn = self.manager.update_last_seen(node_id)
        if conn:
            logger.debug(f"[HeartbeatService] Processed heartbeat from node '{node_id}'")
            return True
        return False
