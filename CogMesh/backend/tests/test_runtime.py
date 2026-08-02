"""Comprehensive unit and integration tests for Runtime Orchestrator, TaskStateMachine, Queue, and REST endpoints."""

import uuid
import pytest
from httpx import AsyncClient

from app.core.exceptions import WorkflowException
from app.domain.execution_context import ExecutionContext
from app.domain.structured_goal import StructuredGoal
from app.runtime.enums import RuntimeEventType, RuntimeStatus, TaskState
from app.runtime.events import RuntimeEvent
from app.runtime.executor import FakeExecutor

from app.runtime.orchestrator import RuntimeOrchestrator
from app.runtime.queue import ExecutionQueue
from app.runtime.state_machine import TaskStateMachine
from app.scheduler.assignment import TaskAssignment
from app.scheduler.planner import ExecutionPlan
from app.workflow.dag import ExecutionDAG
from app.workflow.enums import TaskType


def test_task_state_machine_valid_transitions() -> None:
    """Test valid lifecycle state transitions in TaskStateMachine."""
    assert TaskStateMachine.can_transition(TaskState.PENDING, TaskState.READY)
    assert TaskStateMachine.can_transition(TaskState.READY, TaskState.RUNNING)
    assert TaskStateMachine.can_transition(TaskState.RUNNING, TaskState.COMPLETED)
    assert TaskStateMachine.can_transition(TaskState.RUNNING, TaskState.FAILED)
    assert TaskStateMachine.can_transition(TaskState.PENDING, TaskState.CANCELLED)

    state = TaskStateMachine.transition(TaskState.PENDING, TaskState.READY)
    assert state == TaskState.READY


def test_task_state_machine_invalid_transition_raises() -> None:
    """Test forbidden state transitions raise WorkflowException."""
    assert not TaskStateMachine.can_transition(TaskState.COMPLETED, TaskState.RUNNING)
    with pytest.raises(WorkflowException) as exc_info:
        TaskStateMachine.transition(TaskState.COMPLETED, TaskState.RUNNING)
    assert "Invalid task state transition" in str(exc_info.value.message)


def test_execution_queue_fifo_operations() -> None:
    """Test ExecutionQueue FIFO enqueue, dequeue, size, and clear behavior."""
    queue = ExecutionQueue()
    assert queue.is_empty()
    assert queue.size() == 0

    item1 = TaskAssignment(node_id="n1", device_id="d1", task_type=TaskType.OCR, reason="R1")
    item2 = TaskAssignment(node_id="n2", device_id="d2", task_type=TaskType.SUMMARIZATION, reason="R2")

    queue.enqueue(item1)
    queue.enqueue(item2)

    assert queue.size() == 2
    assert not queue.is_empty()

    popped1 = queue.dequeue()
    assert popped1 is not None
    assert popped1.node_id == "n1"

    popped2 = queue.dequeue()
    assert popped2 is not None
    assert popped2.node_id == "n2"

    assert queue.is_empty()
    assert queue.dequeue() is None

    queue.enqueue(item1)
    queue.clear()
    assert queue.is_empty()


@pytest.mark.asyncio
async def test_fake_executor_simulation() -> None:
    """Test FakeExecutor task simulation returns mock result and telemetry metrics."""
    assignment = TaskAssignment(node_id="n1", device_id="d1", task_type=TaskType.OCR, reason="R1")
    context = ExecutionContext(goal_id="g1")

    res = await FakeExecutor.execute_task(assignment, context, simulated_delay=0.01)

    assert res["node_id"] == "n1"
    assert res["status"] == "COMPLETED"
    assert "confidence" in res["output"]
    assert res["metrics"]["execution_time_ms"] > 0.0


def test_runtime_event_emission() -> None:
    """Test RuntimeOrchestrator.emit_event appends RuntimeEvent to ExecutionContext."""
    context = ExecutionContext(goal_id="g1")
    event = RuntimeOrchestrator.emit_event(
        context,
        RuntimeEventType.PLAN_STARTED,
        "Started plan execution",
    )
    assert event.event_type == RuntimeEventType.PLAN_STARTED
    assert len(context.events) == 1
    assert context.events[0].message == "Started plan execution"


@pytest.mark.asyncio
async def test_runtime_orchestrator_execution_flow() -> None:
    """Test full execution flow through RuntimeOrchestrator."""
    goal_id = str(uuid.uuid4())
    goal = StructuredGoal(goal_id=goal_id, natural_language_input="OCR text", operations=["OCR"])
    dag = ExecutionDAG(goal_id=goal_id)

    assignment = TaskAssignment(node_id="node-1", device_id="dev-1", task_type=TaskType.OCR, reason="Test")
    plan = ExecutionPlan(goal_id=goal_id, workflow_id=dag.dag_id, assignments=[assignment])

    context = await RuntimeOrchestrator.execute_plan(plan, goal, dag, simulated_delay=0.01)

    assert context.status == RuntimeStatus.COMPLETED
    assert context.task_states["node-1"] == TaskState.COMPLETED.value
    assert "node-1" in context.results
    assert "node-1" in context.metrics
    assert len(context.events) >= 4  # PLAN_STARTED, TASK_READY, TASK_STARTED, TASK_COMPLETED, PLAN_COMPLETED


def test_runtime_orchestrator_cancellation() -> None:
    """Test cancelling active context transitions pending tasks to CANCELLED state."""
    context_id = str(uuid.uuid4())
    context = ExecutionContext(
        context_id=context_id,
        goal_id="g1",
        status=RuntimeStatus.RUNNING,
        task_states={"n1": TaskState.PENDING.value, "n2": TaskState.READY.value},
    )
    RuntimeOrchestrator.active_contexts[context_id] = context

    updated = RuntimeOrchestrator.cancel_execution(context_id)

    assert updated.status == RuntimeStatus.CANCELLED
    assert updated.task_states["n1"] == TaskState.CANCELLED.value
    assert updated.task_states["n2"] == TaskState.CANCELLED.value


@pytest.mark.asyncio
async def test_runtime_api_full_flow(client: AsyncClient) -> None:
    """Test REST API full flow: register device, capability, parse goal, generate workflow, schedule plan, and execute runtime."""
    # 1. Register device & report capability
    dev_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Runtime Node", "device_type": "LAPTOP", "ip_address": "192.168.1.100"
    })
    dev_id = dev_res.json()["device_id"]

    await client.post("/api/v1/capabilities/report", json={
        "device_id": dev_id, "cpu_cores": 8, "ram_gb": 16.0, "battery_level": 90.0, "supported_tasks": ["OCR", "SUMMARIZATION"]
    })

    # 2. Parse Goal, Generate Workflow, Generate ExecutionPlan
    goal_res = await client.post("/api/v1/goals/parse", json={"goal": "Perform OCR on image and summarize text."})
    goal_id = goal_res.json()["goal_id"]

    await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})
    await client.post("/api/v1/scheduler/plan", json={"goal_id": goal_id})

    # 3. Start Runtime Execution
    run_res = await client.post("/api/v1/runtime/start", json={"goal_id": goal_id})
    assert run_res.status_code == 200
    context_data = run_res.json()

    assert context_data["goal_id"] == goal_id
    assert context_data["status"] == "COMPLETED"
    assert len(context_data["results"]) == 2
    context_id = context_data["context_id"]

    # 4. Get Status
    status_res = await client.get(f"/api/v1/runtime/status/{context_id}")
    assert status_res.status_code == 200
    assert status_res.json()["context_id"] == context_id

    # 5. Cancel Execution endpoint test
    cancel_res = await client.post(f"/api/v1/runtime/cancel/{context_id}")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_runtime_api_unknown_goal_404(client: AsyncClient) -> None:
    """Test POST /api/v1/runtime/start with non-existent goal returns HTTP 404 Not Found."""
    fake_goal_id = str(uuid.uuid4())
    res = await client.post("/api/v1/runtime/start", json={"goal_id": fake_goal_id})
    assert res.status_code == 404
    assert res.json()["error"] == "GoalNotFoundException"


@pytest.mark.asyncio
async def test_runtime_api_unknown_context_404(client: AsyncClient) -> None:
    """Test GET /api/v1/runtime/status/{context_id} with non-existent context returns HTTP 404 Not Found."""
    fake_ctx_id = str(uuid.uuid4())
    res = await client.get(f"/api/v1/runtime/status/{fake_ctx_id}")
    assert res.status_code == 404
    assert res.json()["error"] == "EntityNotFoundException"


@pytest.mark.asyncio
async def test_runtime_api_cancel_unknown_context_404(client: AsyncClient) -> None:
    """Test POST /api/v1/runtime/cancel/{context_id} with non-existent context returns HTTP 404 Not Found."""
    fake_ctx_id = str(uuid.uuid4())
    res = await client.post(f"/api/v1/runtime/cancel/{fake_ctx_id}")
    assert res.status_code == 404
    assert res.json()["error"] == "EntityNotFoundException"


def test_runtime_status_enum_values() -> None:
    """Test RuntimeStatus enum values."""
    assert RuntimeStatus.IDLE.value == "IDLE"
    assert RuntimeStatus.RUNNING.value == "RUNNING"
    assert RuntimeStatus.COMPLETED.value == "COMPLETED"
    assert RuntimeStatus.FAILED.value == "FAILED"
    assert RuntimeStatus.CANCELLED.value == "CANCELLED"


def test_runtime_event_payload_handling() -> None:
    """Test RuntimeEvent payload data encapsulation."""
    event = RuntimeEvent(
        event_type=RuntimeEventType.TASK_COMPLETED,
        context_id="ctx-1",
        goal_id="g-1",
        message="Task complete",
        payload={"execution_time_ms": 12.5, "power_consumed": 0.5},
    )
    assert event.payload["execution_time_ms"] == 12.5
    assert event.payload["power_consumed"] == 0.5


def test_execution_queue_empty_dequeue_returns_none() -> None:
    """Test popping from empty ExecutionQueue returns None without raising errors."""
    q = ExecutionQueue()
    assert q.dequeue() is None


@pytest.mark.asyncio
async def test_fake_executor_default_task_type() -> None:
    """Test FakeExecutor handles custom task types gracefully."""
    assignment = TaskAssignment(node_id="n-custom", device_id="d-custom", task_type=TaskType.UNKNOWN, reason="Test custom")
    context = ExecutionContext(goal_id="g1")

    res = await FakeExecutor.execute_task(assignment, context, simulated_delay=0.01)
    assert res["status"] == "COMPLETED"
    assert "output" in res["output"]


@pytest.mark.asyncio
async def test_runtime_orchestrator_failed_task_handling() -> None:
    """Test RuntimeOrchestrator handles simulated task failure gracefully."""
    goal_id = str(uuid.uuid4())
    goal = StructuredGoal(goal_id=goal_id, natural_language_input="Fail task", operations=["OCR"])
    dag = ExecutionDAG(goal_id=goal_id)
    assignment = TaskAssignment(node_id="node-fail", device_id="dev-fail", task_type=TaskType.OCR, reason="Test fail")
    plan = ExecutionPlan(goal_id=goal_id, workflow_id=dag.dag_id, assignments=[assignment])

    # Monkeypatch FakeExecutor to raise an exception
    async def mock_fail_task(*args, **kwargs):
        raise RuntimeError("Simulated execution hardware fault")

    original_execute = FakeExecutor.execute_task
    FakeExecutor.execute_task = mock_fail_task
    try:
        context = await RuntimeOrchestrator.execute_plan(plan, goal, dag, simulated_delay=0.01)
        assert context.status == RuntimeStatus.FAILED
        assert context.task_states["node-fail"] == TaskState.FAILED.value
    finally:
        FakeExecutor.execute_task = original_execute

