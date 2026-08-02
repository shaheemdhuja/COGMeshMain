"""Comprehensive End-to-End System Integration Test validating Sprints 1 through 9.

Validates complete execution pipeline:
Device Registry -> Capability Registry -> Goal Service -> Workflow Generator ->
Adaptive Scheduler -> Runtime Orchestrator -> Communication Layer -> Task Adapter Layer.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.communication.enums import MessageType
from app.communication.protocol import create_message
from app.domain.execution_context import ExecutionContext
from app.models.capability import Capability
from app.models.connection_log import ConnectionLog
from app.models.device import Device
from app.models.goal import Goal
from app.models.message_log import MessageLog
from app.models.metric import ExecutionMetric
from app.models.task import Task
from app.models.task_execution_audit import TaskExecutionAudit
from app.models.task_log import TaskLog
from app.models.workflow import Workflow
from app.runtime.enums import RuntimeStatus, TaskState
from app.services.communication_service import CommunicationService
from app.tasks.registry import TaskRegistry


@pytest.mark.asyncio
async def test_complete_cogmesh_end_to_end_pipeline(client: AsyncClient, db_session: AsyncSession) -> None:
    """Execute complete multi-device CogMesh pipeline from NL goal input to persistent results and audit logs."""
    # -------------------------------------------------------------------------
    # STEP 1: Device Registration (Sprint 2)
    # -------------------------------------------------------------------------
    laptop_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Workstation Alpha",
        "device_type": "LAPTOP",
        "ip_address": "192.168.1.10",
        "port": 8000,
        "platform": "windows",
    })
    assert laptop_res.status_code == 201
    laptop_id = laptop_res.json()["device_id"]

    phone_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Edge Phone Beta",
        "device_type": "PHONE",
        "ip_address": "192.168.1.11",
        "port": 8000,
        "platform": "android",
    })
    assert phone_res.status_code == 201
    phone_id = phone_res.json()["device_id"]

    # -------------------------------------------------------------------------
    # STEP 2: Capability Snapshot Reporting (Sprint 3)
    # -------------------------------------------------------------------------
    cap1_res = await client.post("/api/v1/capabilities/report", json={
        "device_id": laptop_id,
        "cpu_cores": 16,
        "ram_gb": 32.0,
        "battery_level": 95.0,
        "network_quality": "EXCELLENT",
        "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION", "MCQ_GENERATION"],
    })
    assert cap1_res.status_code == 200

    cap2_res = await client.post("/api/v1/capabilities/report", json={
        "device_id": phone_id,
        "cpu_cores": 8,
        "ram_gb": 6.0,
        "battery_level": 80.0,
        "network_quality": "GOOD",
        "supported_tasks": ["OCR", "TRANSLATION"],
    })
    assert cap2_res.status_code == 200

    # -------------------------------------------------------------------------
    # STEP 3: Mesh Communication Connection Setup (Sprint 8)
    # -------------------------------------------------------------------------
    conn_laptop = await CommunicationService.register_node(db_session, laptop_id)
    conn_phone = await CommunicationService.register_node(db_session, phone_id)
    assert conn_laptop.node_id == laptop_id
    assert conn_phone.node_id == phone_id

    # Verify active connections via REST API
    conn_res = await client.get("/api/v1/communication/connections")
    assert conn_res.status_code == 200
    active_conns = conn_res.json()
    assert len(active_conns) >= 2

    # -------------------------------------------------------------------------
    # STEP 4: Natural Language Goal Parsing (Sprint 4)
    # -------------------------------------------------------------------------
    goal_res = await client.post("/api/v1/goals/parse", json={
        "goal": "Perform OCR on lecture PDF, summarize text, translate to Spanish and generate MCQs."
    })
    assert goal_res.status_code == 200
    goal_data = goal_res.json()
    goal_id = goal_data["goal_id"]
    assert len(goal_data["operations"]) == 4

    # -------------------------------------------------------------------------
    # STEP 5: ExecutionDAG Workflow Generation & Optimization (Sprint 5)
    # -------------------------------------------------------------------------
    wf_res = await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})
    assert wf_res.status_code == 200
    dag_data = wf_res.json()
    assert len(dag_data["nodes"]) == 4
    assert len(dag_data["edges"]) == 3

    # -------------------------------------------------------------------------
    # STEP 6: Adaptive Scheduler Execution Planning (Sprint 6)
    # -------------------------------------------------------------------------
    plan_res = await client.post("/api/v1/scheduler/plan", json={"goal_id": goal_id})
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert len(plan_data["assignments"]) == 4

    # Transmit TASK_ASSIGNMENT protocol messages across Communication Layer
    for assignment in plan_data["assignments"]:
        msg = create_message(
            message_type=MessageType.TASK_ASSIGNMENT,
            source_node="ORCHESTRATOR",
            destination_node=assignment["device_id"],
            payload=assignment,
        )
        await CommunicationService.send_message(db_session, msg)

    # -------------------------------------------------------------------------
    # STEP 7 & 8: Runtime Orchestration & AI Task Adapters Execution (Sprint 7 & 9)
    # -------------------------------------------------------------------------
    run_res = await client.post("/api/v1/runtime/start", json={"goal_id": goal_id})
    assert run_res.status_code == 200
    context_data = run_res.json()

    # -------------------------------------------------------------------------
    # STEP 9: Verify RuntimeEvents Emitted
    # -------------------------------------------------------------------------
    events = context_data["events"]
    assert len(events) >= 5
    event_types = [e["event_type"] for e in events]
    assert "PLAN_STARTED" in event_types
    assert "TASK_READY" in event_types
    assert "TASK_STARTED" in event_types
    assert "TASK_COMPLETED" in event_types
    assert "PLAN_COMPLETED" in event_types

    # -------------------------------------------------------------------------
    # STEP 10: Verify ExecutionContext Final State
    # -------------------------------------------------------------------------
    assert context_data["status"] == "COMPLETED"
    for node_id, state in context_data["task_states"].items():
        assert state == "COMPLETED"

    # -------------------------------------------------------------------------
    # STEP 11: Verify TaskResults Generated
    # -------------------------------------------------------------------------
    results = context_data["results"]
    assert len(results) == 4
    for node_id, res_payload in results.items():
        assert isinstance(res_payload, dict)

    metrics = context_data["metrics"]
    assert len(metrics) == 4

    # -------------------------------------------------------------------------
    # STEP 12 & 13: Verify Audit Records Persisted in SQLite Database
    # -------------------------------------------------------------------------
    # Check Device table
    dev_db = (await db_session.execute(select(Device).where(Device.id == laptop_id))).scalar_one_or_none()
    assert dev_db is not None

    # Check Capability table
    cap_db = (await db_session.execute(select(Capability).where(Capability.device_id == laptop_id))).scalar_one_or_none()
    assert cap_db is not None

    # Check Goal table
    goal_db = (await db_session.execute(select(Goal).where(Goal.id == goal_id))).scalar_one_or_none()
    assert goal_db is not None

    # Check Workflow table
    wf_db = (await db_session.execute(select(Workflow).where(Workflow.goal_id == goal_id))).scalar_one_or_none()
    assert wf_db is not None

    # Check Task assignments table
    tasks_db = (await db_session.execute(select(Task).where(Task.workflow_id == dag_data["dag_id"]))).scalars().all()
    assert len(tasks_db) == 4

    # Check TaskLog entries table
    logs_db = (await db_session.execute(select(TaskLog))).scalars().all()
    assert len(logs_db) >= 4

    # Check ExecutionMetric entries table
    metrics_db = (await db_session.execute(select(ExecutionMetric).where(ExecutionMetric.goal_id == goal_id))).scalars().all()
    assert len(metrics_db) == 4

    # Check ConnectionLog table
    conn_logs_db = (await db_session.execute(select(ConnectionLog))).scalars().all()
    assert len(conn_logs_db) >= 2

    # Check MessageLog table
    msg_logs_db = (await db_session.execute(select(MessageLog))).scalars().all()
    assert len(msg_logs_db) >= 4

    # Check TaskAdapter list API endpoint
    tasks_api_res = await client.get("/api/v1/tasks")
    assert tasks_api_res.status_code == 200
    assert len(tasks_api_res.json()) >= 4
