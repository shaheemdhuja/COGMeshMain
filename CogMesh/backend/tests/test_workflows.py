"""Comprehensive unit and integration tests for Workflow Generator, Optimizer, DAG, and REST API."""

import uuid
import pytest
from httpx import AsyncClient

from app.core.exceptions import MissingCapabilityException, WorkflowException
from app.domain.structured_goal import StructuredGoal
from app.models.capability import Capability
from app.workflow.dag import ExecutionDAG
from app.workflow.edge import ExecutionEdge
from app.workflow.enums import TaskType
from app.workflow.generator import WorkflowGenerator
from app.workflow.node import ExecutionNode
from app.workflow.optimizer import WorkflowOptimizer


def test_topological_sort_and_cycle_detection() -> None:
    """Test valid topological sorting and cycle detection in ExecutionDAG."""
    dag = ExecutionDAG(goal_id="test-goal-1")

    n1 = ExecutionNode(task_type=TaskType.OCR, required_capabilities=["OCR"])
    n2 = ExecutionNode(task_type=TaskType.SUMMARIZATION, required_capabilities=["SUMMARIZATION"])
    n3 = ExecutionNode(task_type=TaskType.TRANSLATION, required_capabilities=["TRANSLATION"])

    dag.add_node(n1)
    dag.add_node(n2)
    dag.add_node(n3)

    dag.add_edge(ExecutionEdge(source=n1.node_id, destination=n2.node_id))
    dag.add_edge(ExecutionEdge(source=n2.node_id, destination=n3.node_id))

    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == 3
    assert sorted_nodes[0].node_id == n1.node_id
    assert sorted_nodes[1].node_id == n2.node_id
    assert sorted_nodes[2].node_id == n3.node_id

    # Introduce a cycle: n3 -> n1
    dag.add_edge(ExecutionEdge(source=n3.node_id, destination=n1.node_id))
    with pytest.raises(WorkflowException, match="Cycle detected"):
        dag.topological_sort()


def test_workflow_optimizer_duplicate_removal() -> None:
    """Test WorkflowOptimizer merges consecutive duplicate task nodes."""
    dag = ExecutionDAG(goal_id="test-goal-2")

    n1 = ExecutionNode(task_type=TaskType.OCR, required_capabilities=["OCR"])
    n2 = ExecutionNode(task_type=TaskType.OCR, required_capabilities=["OCR"])  # Duplicate OCR
    n3 = ExecutionNode(task_type=TaskType.SUMMARIZATION, required_capabilities=["SUMMARIZATION"])

    dag.add_node(n1)
    dag.add_node(n2)
    dag.add_node(n3)

    dag.add_edge(ExecutionEdge(source=n1.node_id, destination=n2.node_id))
    dag.add_edge(ExecutionEdge(source=n2.node_id, destination=n3.node_id))

    optimized_dag = WorkflowOptimizer.optimize(dag)
    assert len(optimized_dag.nodes) == 2
    task_types = [node.task_type for node in optimized_dag.topological_sort()]
    assert task_types == [TaskType.OCR, TaskType.SUMMARIZATION]


def test_generator_missing_ocr_capability_raises_409() -> None:
    """Test WorkflowGenerator raises MissingCapabilityException when OCR capability is missing in mesh."""
    goal = StructuredGoal(
        natural_language_input="Perform OCR and summarize",
        operations=["OCR", "SUMMARIZATION"],
    )

    # Capability list with ONLY SUMMARIZATION
    caps = [
        Capability(
            device_id=str(uuid.uuid4()),
            cpu_cores=4,
            ram_gb=8.0,
            battery_level=100.0,
            supported_tasks=["SUMMARIZATION"],
        )
    ]

    with pytest.raises(MissingCapabilityException) as exc_info:
        WorkflowGenerator.generate(goal, caps)

    assert exc_info.value.status_code == 409
    assert exc_info.value.details["missing_capability"] == "OCR"


def test_generator_missing_translation_capability_raises_409() -> None:
    """Test WorkflowGenerator raises MissingCapabilityException when TRANSLATION is missing."""
    goal = StructuredGoal(
        natural_language_input="Summarize and translate to Spanish",
        operations=["SUMMARIZATION", "TRANSLATION"],
    )

    caps = [
        Capability(
            device_id=str(uuid.uuid4()),
            cpu_cores=4,
            ram_gb=8.0,
            battery_level=100.0,
            supported_tasks=["SUMMARIZATION"],
        )
    ]

    with pytest.raises(MissingCapabilityException) as exc_info:
        WorkflowGenerator.generate(goal, caps)

    assert exc_info.value.status_code == 409
    assert exc_info.value.details["missing_capability"] == "TRANSLATION"


@pytest.mark.asyncio
async def test_generate_workflow_api_full_lecture_pipeline(client: AsyncClient) -> None:
    """Test full lecture processing workflow generation via REST API."""
    # 1. Register device and report ALL required capabilities
    dev_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Full Node", "device_type": "LAPTOP", "ip_address": "192.168.1.200"
    })
    device_id = dev_res.json()["device_id"]

    await client.post("/api/v1/capabilities/report", json={
        "device_id": device_id,
        "cpu_cores": 16,
        "ram_gb": 32.0,
        "battery_level": 100.0,
        "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION", "MCQ_GENERATION"],
    })

    # 2. Parse Goal
    goal_res = await client.post("/api/v1/goals/parse", json={
        "goal": "Summarize this lecture PDF, translate to French and generate MCQs."
    })
    assert goal_res.status_code == 200
    goal_id = goal_res.json()["goal_id"]

    # 3. Generate Workflow
    wf_res = await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})
    assert wf_res.status_code == 200
    dag_data = wf_res.json()

    assert dag_data["goal_id"] == goal_id
    assert len(dag_data["nodes"]) == 4  # OCR, SUMMARIZATION, TRANSLATION, MCQ_GENERATION
    assert len(dag_data["edges"]) == 3

    # 4. GET Workflow by goal_id
    get_wf_res = await client.get(f"/api/v1/workflows/{goal_id}")
    assert get_wf_res.status_code == 200
    assert get_wf_res.json()["dag_id"] == dag_data["dag_id"]


@pytest.mark.asyncio
async def test_generate_workflow_api_missing_capability_409(client: AsyncClient) -> None:
    """Test REST API returns 409 Conflict when a required capability is missing in the active mesh."""
    # 1. Register device with ONLY OCR
    dev_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Limited Node", "device_type": "PHONE", "ip_address": "192.168.1.201"
    })
    device_id = dev_res.json()["device_id"]

    await client.post("/api/v1/capabilities/report", json={
        "device_id": device_id,
        "cpu_cores": 4,
        "ram_gb": 4.0,
        "battery_level": 80.0,
        "supported_tasks": ["OCR"],
    })

    # 2. Parse Goal requiring SUMMARIZATION
    goal_res = await client.post("/api/v1/goals/parse", json={
        "goal": "Perform OCR on PDF and summarize text."
    })
    goal_id = goal_res.json()["goal_id"]

    # 3. Generate Workflow -> 409 Conflict
    wf_res = await client.post("/api/v1/workflows/generate", json={"goal_id": goal_id})
    assert wf_res.status_code == 409
    err = wf_res.json()
    assert err["error"] == "MissingCapabilityException"
    assert err["details"]["missing_capability"] == "SUMMARIZATION"


@pytest.mark.asyncio
async def test_generate_workflow_unknown_goal_404(client: AsyncClient) -> None:
    """Test generating workflow for non-existent goal returns HTTP 404 Not Found."""
    fake_goal_id = str(uuid.uuid4())
    response = await client.post("/api/v1/workflows/generate", json={"goal_id": fake_goal_id})
    assert response.status_code == 404
    assert response.json()["error"] == "GoalNotFoundException"


@pytest.mark.asyncio
async def test_get_workflow_missing_404(client: AsyncClient) -> None:
    """Test GET /api/v1/workflows/{goal_id} returns 404 if workflow is not generated."""
    # Goal exists but no workflow generated yet
    goal_res = await client.post("/api/v1/goals/parse", json={
        "goal": "Summarize this lecture PDF."
    })
    goal_id = goal_res.json()["goal_id"]

    get_res = await client.get(f"/api/v1/workflows/{goal_id}")
    assert get_res.status_code == 404
    assert get_res.json()["error"] == "EntityNotFoundException"
