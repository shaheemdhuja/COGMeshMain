"""Comprehensive unit and integration tests for Mesh Communication Layer, Transport interface, and API endpoints."""

import datetime
import pytest
from httpx import AsyncClient

from app.communication.connection_manager import ConnectionManager
from app.communication.enums import ConnectionStatus, MessageType, TransportType
from app.communication.heartbeat import CommunicationHeartbeatService
from app.communication.message import Connection, RuntimeMessage
from app.communication.protocol import (
    ProtocolException,
    create_message,
    deserialize_message,
    serialize_message,
)
from app.communication.websocket_adapter import WebSocketAdapter
from app.services.communication_service import CommunicationService


def test_runtime_message_model_serialization() -> None:
    """Test RuntimeMessage creation and JSON serialization."""
    msg = create_message(
        message_type=MessageType.TASK_ASSIGNMENT,
        source_node="ORCHESTRATOR",
        destination_node="node-100",
        payload={"task_id": "t-1", "task_type": "OCR"},
    )
    assert msg.message_id is not None
    assert msg.message_type == MessageType.TASK_ASSIGNMENT
    assert msg.source_node == "ORCHESTRATOR"
    assert msg.destination_node == "node-100"

    json_str = serialize_message(msg)
    assert "TASK_ASSIGNMENT" in json_str

    deserialized = deserialize_message(json_str)
    assert deserialized.message_id == msg.message_id
    assert deserialized.payload["task_id"] == "t-1"


def test_protocol_invalid_json_raises() -> None:
    """Test deserializing invalid JSON raises ProtocolException."""
    with pytest.raises(ProtocolException):
        deserialize_message("invalid json content")


def test_connection_manager_registration() -> None:
    """Test ConnectionManager registering and retrieving nodes."""
    cm = ConnectionManager()
    conn = Connection(node_id="node-1", transport=TransportType.WEBSOCKET)

    registered = cm.register_connection(conn)
    assert registered.status == ConnectionStatus.CONNECTED
    assert cm.get_connection("node-1") is not None
    assert len(cm.get_all_connections()) == 1


def test_connection_manager_lookup_and_removal() -> None:
    """Test lookup and removal of node connections."""
    cm = ConnectionManager()
    conn = Connection(node_id="node-2")
    cm.register_connection(conn)

    removed = cm.remove_connection("node-2")
    assert removed is not None
    assert removed.status == ConnectionStatus.DISCONNECTED
    assert cm.get_connection("node-2") is None


def test_connection_manager_update_last_seen() -> None:
    """Test updating last_seen timestamp refreshes stale connection status."""
    cm = ConnectionManager()
    conn = Connection(node_id="node-3", status=ConnectionStatus.STALE)
    cm.register_connection(conn)
    conn.status = ConnectionStatus.STALE

    refreshed = cm.update_last_seen("node-3")
    assert refreshed is not None
    assert refreshed.status == ConnectionStatus.CONNECTED


@pytest.mark.asyncio
async def test_websocket_adapter_connect_and_disconnect() -> None:
    """Test WebSocketAdapter connect and disconnect workflow."""
    adapter = WebSocketAdapter()
    conn = await adapter.connect("node-10")
    assert conn.node_id == "node-10"
    assert adapter.manager.get_connection("node-10") is not None

    await adapter.disconnect("node-10")
    assert adapter.manager.get_connection("node-10") is None


@pytest.mark.asyncio
async def test_websocket_adapter_send_and_receive() -> None:
    """Test WebSocketAdapter message send and queue receive."""
    adapter = WebSocketAdapter()
    await adapter.connect("node-A")
    await adapter.connect("node-B")

    msg = create_message(
        message_type=MessageType.TASK_ASSIGNMENT,
        source_node="node-A",
        destination_node="node-B",
        payload={"data": "hello"},
    )

    success = await adapter.send(msg)
    assert success is True

    rcvd = await adapter.receive("node-B")
    assert rcvd is not None
    assert rcvd.payload["data"] == "hello"
    assert (await adapter.receive("node-B")) is None



@pytest.mark.asyncio
async def test_websocket_adapter_broadcast() -> None:
    """Test broadcasting message to all connected nodes."""
    adapter = WebSocketAdapter()
    await adapter.connect("n1")
    await adapter.connect("n2")

    bcast_msg = create_message(
        message_type=MessageType.PING,
        source_node="ORCHESTRATOR",
        destination_node="BROADCAST",
    )

    count = await adapter.broadcast(bcast_msg)
    assert count == 2

    assert (await adapter.receive("n1")) is not None
    assert (await adapter.receive("n2")) is not None


def test_heartbeat_service_stale_detection() -> None:
    """Test CommunicationHeartbeatService marking timed out connections as STALE."""
    cm = ConnectionManager()
    conn = Connection(node_id="stale-node")
    # Backdate last_seen to simulate 60s ago
    conn.last_seen = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=60)
    cm._connections["stale-node"] = conn

    hb_service = CommunicationHeartbeatService(cm)
    stale_list = hb_service.check_stale_connections(timeout_seconds=30.0)

    assert "stale-node" in stale_list
    assert conn.status == ConnectionStatus.STALE


def test_heartbeat_service_process_heartbeat() -> None:
    """Test processing heartbeat refreshes timestamp."""
    cm = ConnectionManager()
    conn = Connection(node_id="active-node")
    cm.register_connection(conn)

    hb_service = CommunicationHeartbeatService(cm)
    processed = hb_service.process_heartbeat("active-node")
    assert processed is True


@pytest.mark.asyncio
async def test_communication_service_register_and_send(db_session) -> None:
    """Test CommunicationService registration and message sending with DB audit log."""
    conn = await CommunicationService.register_node(db_session, "service-node-1")
    assert conn.node_id == "service-node-1"

    msg = create_message(
        message_type=MessageType.HEARTBEAT,
        source_node="service-node-1",
        destination_node="ORCHESTRATOR",
    )

    await CommunicationService.send_message(db_session, msg)
    history = CommunicationService.get_recent_messages()
    assert len(history) >= 1


@pytest.mark.asyncio
async def test_communication_api_get_connections(client: AsyncClient) -> None:
    """Test GET /api/v1/communication/connections returns active node connections."""
    res = await client.get("/api/v1/communication/connections")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_communication_api_get_messages(client: AsyncClient) -> None:
    """Test GET /api/v1/communication/messages returns recent message audit logs."""
    res = await client.get("/api/v1/communication/messages")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_connection_status_enum_values() -> None:
    """Test ConnectionStatus enum string values."""
    assert ConnectionStatus.CONNECTED.value == "CONNECTED"
    assert ConnectionStatus.DISCONNECTED.value == "DISCONNECTED"
    assert ConnectionStatus.STALE.value == "STALE"
    assert ConnectionStatus.RECONNECTING.value == "RECONNECTING"


def test_transport_type_enum_values() -> None:
    """Test TransportType enum string values."""
    assert TransportType.WEBSOCKET.value == "WEBSOCKET"
    assert TransportType.HTTP_POLLING.value == "HTTP_POLLING"
    assert TransportType.MOCK_INMEMORY.value == "MOCK_INMEMORY"

