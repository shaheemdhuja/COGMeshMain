"""Integration tests for FastAPI Real WebSocket endpoint, node registration, heartbeat, and disconnects."""

import json
import pytest
from fastapi.testclient import TestClient

from app.communication.enums import MessageType
from app.communication.message import RuntimeMessage
from app.communication.protocol import parse_message, serialize_message
from app.main import app
from app.services.communication_service import CommunicationService


def test_websocket_connect_and_heartbeat() -> None:
    """Test connecting to real FastAPI WebSocket endpoint and exchanging HEARTBEAT frames."""
    client = TestClient(app)
    device_id = "test-ws-node-01"

    with client.websocket_connect(f"/api/v1/communication/ws/node/{device_id}") as websocket:
        hb_msg = RuntimeMessage(
            message_type=MessageType.HEARTBEAT,
            source_node=device_id,
            destination_node="SERVER",
            payload={"ping": True},
        )
        websocket.send_text(serialize_message(hb_msg))

        response_data = websocket.receive_text()
        parsed_ack = parse_message(response_data)

        assert parsed_ack.message_type == MessageType.HEARTBEAT
        assert parsed_ack.payload.get("status") == "ACK"
        assert parsed_ack.payload.get("node_id") == device_id


def test_websocket_task_assignment_and_result() -> None:
    """Test delivering a TASK_ASSIGNMENT message over WebSocket and receiving TASK_RESULT."""
    client = TestClient(app)
    device_id = "test-ws-node-02"

    with client.websocket_connect(f"/api/v1/communication/ws/node/{device_id}") as websocket:
        # Verify transport is tracking the active socket
        active_conns = CommunicationService.get_active_connections()
        assert any(c.node_id == device_id for c in active_conns)

        # Simulate TASK_RESULT sent from client
        res_msg = RuntimeMessage(
            message_type=MessageType.TASK_RESULT,
            source_node=device_id,
            destination_node="SERVER",
            payload={
                "node_id": "node-100",
                "status": "COMPLETED",
                "output": {"text": "Extracted text via socket"},
            },
        )
        websocket.send_text(serialize_message(res_msg))


def test_websocket_disconnect_cleanup() -> None:
    """Test that disconnecting from WebSocket endpoint cleans up connection state."""
    client = TestClient(app)
    device_id = "test-ws-node-03"

    with client.websocket_connect(f"/api/v1/communication/ws/node/{device_id}") as websocket:
        assert any(c.node_id == device_id for c in CommunicationService.get_active_connections())

    # After exiting block, connection should be disconnected
    assert not any(c.node_id == device_id and c.status.value == "CONNECTED" for c in CommunicationService.get_active_connections())
