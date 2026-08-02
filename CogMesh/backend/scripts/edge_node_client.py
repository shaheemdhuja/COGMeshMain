"""CogMesh Remote Edge Node Client.

Connects to CogMesh Runtime Server over WebSockets, maintains periodic heartbeats,
listens for remote TASK_ASSIGNMENT messages, executes tasks via AdapterFactory,
and returns TASK_RESULT frames to the master orchestrator.
"""

import argparse
import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
import websockets

from app.communication.enums import MessageType
from app.communication.message import RuntimeMessage
from app.communication.protocol import parse_message, serialize_message
from app.tasks.factory import AdapterFactory


class EdgeNodeClient:
    """Remote Edge Node Client communicating with CogMesh Runtime master via WebSockets."""

    def __init__(self, server_url: str, device_id: str, device_name: str = "Edge Client Node"):
        self.server_url = server_url.rstrip("/")
        self.device_id = device_id
        self.device_name = device_name
        self.running = True

    async def heartbeat_loop(self, websocket):
        """Send periodic HEARTBEAT frames to master server every 5 seconds."""
        while self.running:
            try:
                hb_msg = RuntimeMessage(
                    message_type=MessageType.HEARTBEAT,
                    source_node=self.device_id,
                    destination_node="SERVER",
                    payload={"device_name": self.device_name, "timestamp": time.time()},
                )
                await websocket.send(serialize_message(hb_msg))
                logger.debug(f"[EdgeNodeClient] Heartbeat sent from node '{self.device_id}'")
                await asyncio.sleep(5.0)
            except Exception as e:
                logger.warning(f"[EdgeNodeClient] Heartbeat loop error: {e}")
                break

    async def handle_task_assignment(self, websocket, message: RuntimeMessage):
        """Execute assigned AI task via AdapterFactory and return TASK_RESULT to server."""
        payload = message.payload or {}
        task_type = payload.get("task_type", "OCR")
        node_id = payload.get("node_id", message.message_id)
        input_data = payload.get("input_data", {})

        logger.info(f"[EdgeNodeClient] Executing remote task '{task_type}' ({node_id})...")
        start_time = time.perf_counter()

        try:
            adapter = AdapterFactory.create_adapter(str(task_type))
            result = await adapter.execute(input_data)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            result_msg = RuntimeMessage(
                message_type=MessageType.TASK_RESULT,
                source_node=self.device_id,
                destination_node="SERVER",
                payload={
                    "node_id": node_id,
                    "task_type": task_type,
                    "status": result.status.value,
                    "output": result.output,
                    "metrics": {
                        "execution_time_ms": elapsed_ms,
                        "adapter_name": result.adapter_name,
                        "provider_name": result.provider_name,
                        "model_name": result.model_name,
                    },
                },
            )
            await websocket.send(serialize_message(result_msg))
            logger.info(f"[EdgeNodeClient] Completed task '{task_type}' in {elapsed_ms}ms and sent TASK_RESULT.")

        except Exception as exc:
            logger.error(f"[EdgeNodeClient] Error executing remote task '{task_type}': {exc}")
            error_msg = RuntimeMessage(
                message_type=MessageType.TASK_RESULT,
                source_node=self.device_id,
                destination_node="SERVER",
                payload={
                    "node_id": node_id,
                    "task_type": task_type,
                    "status": "FAILURE",
                    "output": {"error": str(exc)},
                    "metrics": {"execution_time_ms": 0.0},
                },
            )
            await websocket.send(serialize_message(error_msg))

    async def start(self):
        """Main client loop with automatic reconnection if WebSocket disconnects."""
        ws_endpoint = f"{self.server_url}/api/v1/communication/ws/node/{self.device_id}"
        logger.info(f"[EdgeNodeClient] Starting client '{self.device_name}' ({self.device_id}). Target: {ws_endpoint}")

        while self.running:
            try:
                async with websockets.connect(ws_endpoint) as websocket:
                    logger.info(f"[EdgeNodeClient] Connected to server: {ws_endpoint}")

                    # Start background heartbeat task
                    hb_task = asyncio.create_task(self.heartbeat_loop(websocket))

                    try:
                        async for raw_data in websocket:
                            msg = parse_message(raw_data)
                            logger.info(f"[EdgeNodeClient] Received frame '{msg.message_type.value}'")

                            if msg.message_type == MessageType.TASK_ASSIGNMENT:
                                await self.handle_task_assignment(websocket, msg)

                    finally:
                        hb_task.cancel()

            except Exception as e:
                logger.warning(f"[EdgeNodeClient] Connection error: {e}. Reconnecting in 3 seconds...")
                await asyncio.sleep(3.0)


def main():
    parser = argparse.ArgumentParser(description="CogMesh Remote Edge Node Client")
    parser.add_argument("--server-url", default="ws://127.0.0.1:8000", help="CogMesh Server WebSocket URL")
    parser.add_argument("--device-id", default="edge-node-phone-01", help="Unique Edge Node Device ID")
    parser.add_argument("--device-name", default="Remote Android Phone", help="Human-readable Device Name")
    args = parser.parse_args()

    client = EdgeNodeClient(
        server_url=args.server_url,
        device_id=args.device_id,
        device_name=args.device_name,
    )

    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        logger.info("[EdgeNodeClient] Client stopped by user.")


if __name__ == "__main__":
    main()
