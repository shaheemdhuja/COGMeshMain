"""Comprehensive unit and integration tests for Adaptive Task Scheduler and ExecutionPlan endpoints."""

import uuid
import pytest
from httpx import AsyncClient

from app.core.exceptions import NoEligibleDeviceException
from app.domain.structured_goal import StructuredGoal
from app.models.capability import Capability
from app.models.device import Device
from app.scheduler.assignment import TaskAssignment
from app.scheduler.planner import ExecutionPlan
from app.scheduler.scheduler import AdaptiveScheduler
from app.scheduler.scoring import SchedulingScore
from app.workflow.enums import TaskType
from app.workflow.generator import WorkflowGenerator



def test_scheduling_score_offline_device_rejected() -> None:
    """Test device with OFFLINE status receives 0.0 score."""
    dev = Device(id=str(uuid.uuid4()), device_name="Offline Dev", device_type="LAPTOP", ip_address="10.0.0.1", status="OFFLINE")
    cap = Capability(device_id=dev.id, cpu_cores=8, ram_gb=16.0, battery_level=90.0, supported_tasks=["OCR"])

    score, reason = SchedulingScore.calculate_score(dev, cap, ["OCR"])
    assert score == 0.0
    assert "OFFLINE" in reason


def test_scheduling_score_missing_capability_rejected() -> None:
    """Test device lacking required task capability receives 0.0 score."""
    dev = Device(id=str(uuid.uuid4()), device_name="Online Dev", device_type="PHONE", ip_address="10.0.0.2", status="ONLINE")
    cap = Capability(device_id=dev.id, cpu_cores=4, ram_gb=4.0, battery_level=100.0, supported_tasks=["OCR"])

    # Node requires SUMMARIZATION, but device only supports OCR
    score, reason = SchedulingScore.calculate_score(dev, cap, ["SUMMARIZATION"])
    assert score == 0.0
    assert "lacks required capability" in reason


def test_scheduling_score_weighted_competition() -> None:
    """Test device with higher battery and RAM receives higher score."""
    dev1 = Device(id=str(uuid.uuid4()), device_name="Phone Low Batt", device_type="PHONE", ip_address="10.0.0.3", status="ONLINE")
    cap1 = Capability(device_id=dev1.id, cpu_cores=4, ram_gb=4.0, battery_level=20.0, network_quality="FAIR", supported_tasks=["OCR"])

    dev2 = Device(id=str(uuid.uuid4()), device_name="Laptop Powerful", device_type="LAPTOP", ip_address="10.0.0.4", status="ONLINE")
    cap2 = Capability(device_id=dev2.id, cpu_cores=16, ram_gb=32.0, battery_level=95.0, network_quality="EXCELLENT", supported_tasks=["OCR"])

    score1, _ = SchedulingScore.calculate_score(dev1, cap1, ["OCR"])
    score2, _ = SchedulingScore.calculate_score(dev2, cap2, ["OCR"])

    assert score2 > score1


def test_adaptive_scheduler_no_eligible_device_raises_409() -> None:
    """Test AdaptiveScheduler raises NoEligibleDeviceException when no device is online/capable."""
    goal = StructuredGoal(natural_language_input="Perform OCR", operations=["OCR"])
    dev = Device(id=str(uuid.uuid4()), device_name="Offline Dev", device_type="PHONE", ip_address="10.0.0.5", status="OFFLINE")
    cap = Capability(device_id=dev.id, cpu_cores=4, ram_gb=4.0, battery_level=100.0, supported_tasks=["OCR"])

    dag = WorkflowGenerator.generate(goal, [cap])

    with pytest.raises(NoEligibleDeviceException) as exc_info:
        AdaptiveScheduler.schedule_dag(dag, [dev], [cap])

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_scheduler_api_full_flow(client: AsyncClient) -> None:
    """Test full flow: Register devices, capabilities, goal, generate workflow, and generate ExecutionPlan."""
    # 1. Register 2 devices
    dev1_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Primary Laptop", "device_type": "LAPTOP", "ip_address": "192.168.1.10"
    })
    dev1_id = dev1_res.json()["device_id"]

    dev2_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Secondary Phone", "device_type": "PHONE", "ip_address": "192.168.1.11"
    })
    dev2_id = dev2_res.json()["device_id"]

    # 2. Report Capabilities
    await client.post("/api/v1/capabilities/report", json={
        "device_id": dev1_id,
        "cpu_cores": 16,
        "ram_gb": 32.0,
        "battery_level": 95.0,
        "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION"],
    })

    await client.post("/api/v1/capabilities/report", json={
        "device_id": dev2_id,
        "cpu_cores": 8,
        "ram_gb": 6.0,
        "battery_level": 50.0,
        "supported_tasks": ["OCR", "TRANSLATION"],
    })

    # 3. Parse Goal
    goal_res = await client.post("/api/v1/goals/parse", json={
        "goal": "Perform OCR on PDF, summarize text and translate to Spanish."
    })
    goal_id = goal_res.json()["goal_id"]

    # 4. Generate Workflow DAG
    wf_res = await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})
    assert wf_res.status_code == 200

    # 5. Generate Execution Plan
    plan_res = await client.post("/api/v1/scheduler/plan", json={"goal_id": goal_id})
    assert plan_res.status_code == 200
    plan_data = plan_res.json()

    assert plan_data["goal_id"] == goal_id
    assert len(plan_data["assignments"]) == 3  # OCR, SUMMARIZATION, TRANSLATION

    # Verify SUMMARIZATION task is assigned to dev1 (Primary Laptop) because dev2 lacks SUMMARIZATION
    sum_assignment = next(a for a in plan_data["assignments"] if a["task_type"] == "SUMMARIZATION")
    assert sum_assignment["device_id"] == dev1_id

    # 6. GET /api/v1/scheduler/{goal_id}
    get_plan_res = await client.get(f"/api/v1/scheduler/{goal_id}")
    assert get_plan_res.status_code == 200
    assert get_plan_res.json()["plan_id"] == plan_data["plan_id"]


@pytest.mark.asyncio
async def test_scheduler_api_unknown_goal_404(client: AsyncClient) -> None:
    """Test posting plan request for non-existent goal returns HTTP 404 Not Found."""
    fake_goal_id = str(uuid.uuid4())
    res = await client.post("/api/v1/scheduler/plan", json={"goal_id": fake_goal_id})
    assert res.status_code == 404
    assert res.json()["error"] == "GoalNotFoundException"


@pytest.mark.asyncio
async def test_scheduler_api_no_eligible_device_409(client: AsyncClient) -> None:
    """Test generating plan when candidate device becomes OFFLINE returns HTTP 409 Conflict."""
    # 1. Register device
    dev_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Failing Node", "device_type": "PHONE", "ip_address": "192.168.1.30"
    })
    device_id = dev_res.json()["device_id"]

    await client.post("/api/v1/capabilities/report", json={
        "device_id": device_id,
        "cpu_cores": 4,
        "ram_gb": 4.0,
        "battery_level": 100.0,
        "supported_tasks": ["OCR"],
    })

    # 2. Parse Goal and Generate Workflow
    goal_res = await client.post("/api/v1/goals/parse", json={"goal": "Perform OCR on PDF."})
    goal_id = goal_res.json()["goal_id"]

    await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})

    # 3. Simulate device heartbeat changing status to BUSY/OFFLINE
    await client.post("/api/v1/devices/heartbeat", json={"device_id": device_id, "status": "OFFLINE"})

    # 4. Generate plan -> should fail with 409
    plan_res = await client.post("/api/v1/scheduler/plan", json={"goal_id": goal_id})
    assert plan_res.status_code == 409
    assert plan_res.json()["error"] == "NoEligibleDeviceException"


def test_scheduling_score_tie_breaking() -> None:
    """Test candidate tie breaking where device with higher RAM wins if scores match."""
    dev1 = Device(id=str(uuid.uuid4()), device_name="Node 8GB", device_type="LAPTOP", ip_address="10.0.0.1", status="ONLINE")
    cap1 = Capability(device_id=dev1.id, cpu_cores=8, ram_gb=8.0, battery_level=80.0, network_quality="GOOD", supported_tasks=["OCR"])

    dev2 = Device(id=str(uuid.uuid4()), device_name="Node 16GB", device_type="LAPTOP", ip_address="10.0.0.2", status="ONLINE")
    cap2 = Capability(device_id=dev2.id, cpu_cores=8, ram_gb=16.0, battery_level=80.0, network_quality="GOOD", supported_tasks=["OCR"])

    score1, _ = SchedulingScore.calculate_score(dev1, cap1, ["OCR"])
    score2, _ = SchedulingScore.calculate_score(dev2, cap2, ["OCR"])

    assert score2 > score1


def test_task_assignment_model_serialization() -> None:
    """Test creation and serialization of TaskAssignment model."""
    assignment = TaskAssignment(
        node_id=str(uuid.uuid4()),
        device_id=str(uuid.uuid4()),
        task_type=TaskType.OCR,
        priority=2,
        reason="Selected based on highest score 0.850",
        estimated_duration=2.5,
    )
    assert assignment.assignment_id is not None
    assert assignment.task_type == TaskType.OCR
    assert assignment.priority == 2


def test_execution_plan_domain_model() -> None:
    """Test creation and metadata properties of ExecutionPlan model."""
    goal_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    plan = ExecutionPlan(goal_id=goal_id, workflow_id=workflow_id, assignments=[])
    assert plan.plan_id is not None
    assert plan.goal_id == goal_id
    assert plan.workflow_id == workflow_id
    assert len(plan.assignments) == 0

