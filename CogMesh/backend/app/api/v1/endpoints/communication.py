"""FastAPI REST API and WebSocket endpoints for Mesh Communication Layer."""

from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from loguru import logger

from app.communication.enums import MessageType, ConnectionStatus
from app.communication.message import Connection, RuntimeMessage
from app.communication.protocol import parse_message, serialize_message
from app.services.communication_service import CommunicationService

router = APIRouter(prefix="/communication", tags=["Mesh Communication"])


@router.get(
    "/connections",
    response_model=List[Connection],
    status_code=status.HTTP_200_OK,
    summary="List active Runtime Node connections",
)
async def list_connections() -> List[Connection]:
    """Retrieve all active or managed node connection sessions."""
    return CommunicationService.get_active_connections()


@router.get(
    "/messages",
    response_model=List[RuntimeMessage],
    status_code=status.HTTP_200_OK,
    summary="List recent transmitted RuntimeMessages",
)
async def list_messages() -> List[RuntimeMessage]:
    """Retrieve recent transmitted RuntimeMessage protocol audit logs."""
    return CommunicationService.get_recent_messages()


@router.websocket("/ws/node/{device_id}")
@router.websocket("/ws/{device_id}")
async def websocket_node_endpoint(websocket: WebSocket, device_id: str) -> None:
    """Real FastAPI WebSocket endpoint for edge node registration, heartbeat, and task dispatch."""
    await websocket.accept()
    transport = CommunicationService.get_transport()
    await transport.connect(node_id=device_id, socket=websocket)
    logger.info(f"[WebSocketEndpoint] Real WebSocket connection accepted for node '{device_id}'")

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                message = parse_message(raw_data)
                logger.info(f"[WebSocketEndpoint] Received '{message.message_type.value}' from '{device_id}'")

                # Handle Heartbeat
                if message.message_type == MessageType.HEARTBEAT:
                    transport.manager.update_last_seen(device_id)
                    ack_msg = RuntimeMessage(
                        message_type=MessageType.HEARTBEAT,
                        source_node="SERVER",
                        destination_node=device_id,
                        payload={"status": "ACK", "node_id": device_id},
                    )
                    await websocket.send_text(serialize_message(ack_msg))

                # Handle Task Result returned from remote edge node
                elif message.message_type == MessageType.TASK_RESULT:
                    transport.manager.update_last_seen(device_id)
                    # Enqueue in transport for orchestrator processing
                    await transport.send(message)

                # General message handling
                else:
                    transport.manager.update_last_seen(device_id)

            except Exception as parse_err:
                logger.warning(f"[WebSocketEndpoint] Error parsing socket frame from '{device_id}': {parse_err}")

    except WebSocketDisconnect:
        logger.info(f"[WebSocketEndpoint] Node '{device_id}' disconnected from WebSocket endpoint.")
        await transport.disconnect(device_id)
    except Exception as exc:
        logger.error(f"[WebSocketEndpoint] Unexpected error on socket for node '{device_id}': {exc}")
        await transport.disconnect(device_id)
