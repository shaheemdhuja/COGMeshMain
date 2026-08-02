"""Communication Service managing Transport instances, API requests, and audit log persistence."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.communication.connection_manager import ConnectionManager
from app.communication.message import Connection, RuntimeMessage
from app.communication.protocol import serialize_message
from app.communication.websocket_adapter import WebSocketAdapter
from app.database.repository.base import BaseRepository
from app.models.connection_log import ConnectionLog
from app.models.message_log import MessageLog

# Global singleton WebSocketAdapter and ConnectionManager
_global_connection_manager = ConnectionManager()
_global_transport = WebSocketAdapter(connection_manager=_global_connection_manager)


class CommunicationService:
    """Service layer exposing communication APIs and managing database audit persistence."""

    @classmethod
    def get_transport(cls) -> WebSocketAdapter:
        """Access global transport adapter instance."""
        return _global_transport

    @classmethod
    def get_connection_manager(cls) -> ConnectionManager:
        """Access global connection manager instance."""
        return _global_connection_manager

    @classmethod
    async def register_node(cls, db: AsyncSession, node_id: str) -> Connection:
        """Register a node connection and record connection audit log in SQLite."""
        conn = await _global_transport.connect(node_id)

        # Audit log in SQLite
        conn_log = ConnectionLog(
            node_id=node_id,
            status=conn.status.value,
            transport=conn.transport.value,
        )
        log_repo = BaseRepository[ConnectionLog](ConnectionLog, db)
        await log_repo.create(conn_log)

        return conn

    @classmethod
    async def send_message(cls, db: AsyncSession, message: RuntimeMessage) -> bool:
        """Send message through transport adapter and record message audit log in SQLite."""
        success = await _global_transport.send(message)

        # Audit log in SQLite
        msg_log = MessageLog(
            message_type=message.message_type.value,
            source_node=message.source_node,
            destination_node=message.destination_node,
            payload_json=serialize_message(message),
        )
        msg_repo = BaseRepository[MessageLog](MessageLog, db)
        await msg_repo.create(msg_log)

        return success

    @classmethod
    def get_active_connections(cls) -> List[Connection]:
        """Retrieve list of currently active or managed connections."""
        return _global_connection_manager.get_all_connections()

    @classmethod
    def get_recent_messages(cls) -> List[RuntimeMessage]:
        """Retrieve list of recently transmitted RuntimeMessages from memory history."""
        return _global_transport.get_message_history()
