"""Unit and integration tests for Goal Service, domain models, and API endpoints."""

import pytest
from httpx import AsyncClient

from app.domain.execution_context import ExecutionContext
from app.domain.structured_goal import StructuredGoal
from app.services.goal_service import GoalService


@pytest.mark.asyncio
async def test_parse_goal_api_success(client: AsyncClient) -> None:
    """Test POST /api/v1/goals/parse returns a valid StructuredGoal payload."""
    payload = {"goal": "Summarize this lecture PDF and generate MCQs."}
    response = await client.post("/api/v1/goals/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "goal_id" in data
    assert data["natural_language_input"] == "Summarize this lecture PDF and generate MCQs."
    assert data["goal_type"] == "lecture_processing"
    assert data["input_type"] == "pdf"
    assert "OCR" in data["operations"]
    assert "SUMMARIZATION" in data["operations"]
    assert "MCQ_GENERATION" in data["operations"]


@pytest.mark.asyncio
async def test_parse_goal_full_pipeline(client: AsyncClient) -> None:
    """Test parsing complex goal containing OCR, summarization, translation, and MCQ generation."""
    payload = {
        "goal": "Perform OCR on scanned lecture notes PDF, summarize text, translate to Spanish and generate MCQs."
    }
    response = await client.post("/api/v1/goals/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["operations"] == ["OCR", "SUMMARIZATION", "TRANSLATION", "MCQ_GENERATION"]
    assert data["constraints"].get("target_language") == "Spanish"


@pytest.mark.asyncio
async def test_parse_goal_unknown_operations_422(client: AsyncClient) -> None:
    """Test goal input with no recognizable operations returns HTTP 422 GoalParsingException."""
    payload = {"goal": "Hello world foo bar baz"}
    response = await client.post("/api/v1/goals/parse", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "GoalParsingException"


@pytest.mark.asyncio
async def test_parse_goal_empty_input_422(client: AsyncClient) -> None:
    """Test empty goal string returns HTTP 422 validation error."""
    payload = {"goal": "   "}
    response = await client.post("/api/v1/goals/parse", json=payload)
    assert response.status_code == 422


def test_structured_goal_domain_model() -> None:
    """Test direct creation and serialization of StructuredGoal domain object."""
    sg = StructuredGoal(
        natural_language_input="Test goal",
        goal_type="lecture_processing",
        input_type="pdf",
        operations=["OCR", "SUMMARIZATION"],
        priority=2,
    )
    assert sg.goal_id is not None
    assert sg.priority == 2
    assert sg.operations == ["OCR", "SUMMARIZATION"]


def test_execution_context_domain_model() -> None:
    """Test creation and state tracking of ExecutionContext domain object."""
    sg = StructuredGoal(
        natural_language_input="Test execution context",
        operations=["OCR"],
    )
    ctx = ExecutionContext(
        goal_id=sg.goal_id,
        goal=sg,
        task_states={"task-1": "PENDING"},
    )
    assert ctx.context_id is not None
    assert ctx.goal_id == sg.goal_id
    assert ctx.goal.natural_language_input == "Test execution context"
    assert ctx.task_states["task-1"] == "PENDING"
