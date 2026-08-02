"""Comprehensive unit and integration tests for AI Task Adapter Layer, TaskRegistry, AdapterFactory, and REST API."""

import uuid
import pytest
from httpx import AsyncClient

from app.core.exceptions import WorkflowException
from app.tasks.adapters.mcq_adapter import MCQAdapter
from app.tasks.adapters.ocr_adapter import OCRAdapter
from app.tasks.adapters.summarization_adapter import SummaryAdapter
from app.tasks.adapters.translation_adapter import TranslationAdapter
from app.tasks.enums import TaskStatus
from app.tasks.factory import AdapterFactory
from app.tasks.registry import TaskRegistry
from app.tasks.result import TaskResult


def test_task_registry_registration_and_lookup() -> None:
    """Test registering and looking up task adapters in TaskRegistry."""
    supported = TaskRegistry.get_supported_tasks()
    assert "OCR" in supported
    assert "SUMMARIZATION" in supported

    adapter_cls = TaskRegistry.get_adapter_class("OCR")
    assert adapter_cls is OCRAdapter

    adapters_info = TaskRegistry.list_adapters()
    assert len(adapters_info) >= 4


def test_adapter_factory_create_adapter() -> None:
    """Test AdapterFactory instantiating adapters by task_type key."""
    ocr_adapter = AdapterFactory.create_adapter("OCR")
    assert isinstance(ocr_adapter, OCRAdapter)
    assert ocr_adapter.adapter_name == "OCRAdapter"
    assert ocr_adapter.provider_name == "MockOCRProvider"
    assert ocr_adapter.model_name == "mock-tesseract-v5"

    summary_adapter = AdapterFactory.create_adapter("SUMMARIZATION")
    assert isinstance(summary_adapter, SummaryAdapter)


def test_adapter_factory_unregistered_type_raises() -> None:
    """Test AdapterFactory raises WorkflowException when requesting unregistered task type."""
    with pytest.raises(WorkflowException) as exc_info:
        AdapterFactory.create_adapter("NON_EXISTENT_TASK")
    assert "No AI task adapter registered" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_ocr_adapter_execution() -> None:
    """Test OCRAdapter execution and output validation."""
    adapter = OCRAdapter()
    assert adapter.validate_input({"page": 1}) is True

    result = await adapter.execute({"page": 1})
    assert result.status == TaskStatus.SUCCESS
    assert "text" in result.output
    assert result.adapter_name == "OCRAdapter"
    assert result.provider_name == "MockOCRProvider"
    assert result.model_name == "mock-tesseract-v5"


@pytest.mark.asyncio
async def test_summary_adapter_execution() -> None:
    """Test SummaryAdapter execution and output validation."""
    adapter = SummaryAdapter()
    result = await adapter.execute({"text": "sample"})
    assert result.status == TaskStatus.SUCCESS
    assert "summary" in result.output
    assert adapter.validate_output(result.output) is True


@pytest.mark.asyncio
async def test_translation_adapter_execution() -> None:
    """Test TranslationAdapter execution and output validation."""
    adapter = TranslationAdapter()
    result = await adapter.execute({"target_lang": "Spanish"})
    assert result.status == TaskStatus.SUCCESS
    assert "translated_text" in result.output


@pytest.mark.asyncio
async def test_mcq_adapter_execution() -> None:
    """Test MCQAdapter execution and output validation."""
    adapter = MCQAdapter()
    result = await adapter.execute({})
    assert result.status == TaskStatus.SUCCESS
    assert "questions" in result.output
    assert len(result.output["questions"]) >= 2


def test_task_result_serialization() -> None:
    """Test TaskResult Pydantic model serialization."""
    res = TaskResult(
        adapter_name="OCRAdapter",
        provider_name="MockOCRProvider",
        model_name="mock-tesseract-v5",
        output={"text": "test"},
    )
    assert res.task_id is not None
    assert res.status == TaskStatus.SUCCESS
    json_data = res.model_dump()
    assert json_data["adapter_name"] == "OCRAdapter"


def test_task_status_enum() -> None:
    """Test TaskStatus enum values."""
    assert TaskStatus.SUCCESS.value == "SUCCESS"
    assert TaskStatus.FAILURE.value == "FAILURE"
    assert TaskStatus.INVALID_INPUT.value == "INVALID_INPUT"


@pytest.mark.asyncio
async def test_tasks_api_list_adapters(client: AsyncClient) -> None:
    """Test GET /api/v1/tasks returns registered adapter metadata list."""
    res = await client.get("/api/v1/tasks")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    ocr_info = next(item for item in data if item["task_type"] == "OCR")
    assert ocr_info["adapter_name"] == "OCRAdapter"


@pytest.mark.asyncio
async def test_tasks_api_execute_task_ocr(client: AsyncClient) -> None:
    """Test POST /api/v1/tasks/execute with OCR task."""
    res = await client.post("/api/v1/tasks/execute", json={
        "task_type": "OCR",
        "input_data": {"page": 1}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["adapter_name"] == "OCRAdapter"
    assert data["provider_name"] == "MockOCRProvider"
    assert "text" in data["output"]


@pytest.mark.asyncio
async def test_tasks_api_execute_task_summary(client: AsyncClient) -> None:
    """Test POST /api/v1/tasks/execute with SUMMARIZATION task."""
    res = await client.post("/api/v1/tasks/execute", json={
        "task_type": "SUMMARIZATION",
        "input_data": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["adapter_name"] == "SummaryAdapter"
    assert "summary" in data["output"]


@pytest.mark.asyncio
async def test_tasks_api_execute_task_translation(client: AsyncClient) -> None:
    """Test POST /api/v1/tasks/execute with TRANSLATION task."""
    res = await client.post("/api/v1/tasks/execute", json={
        "task_type": "TRANSLATION",
        "input_data": {"target_lang": "Spanish"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["adapter_name"] == "TranslationAdapter"
    assert "translated_text" in data["output"]


@pytest.mark.asyncio
async def test_tasks_api_execute_task_mcq(client: AsyncClient) -> None:
    """Test POST /api/v1/tasks/execute with MCQ_GENERATION task."""
    res = await client.post("/api/v1/tasks/execute", json={
        "task_type": "MCQ_GENERATION",
        "input_data": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["adapter_name"] == "MCQAdapter"
    assert "questions" in data["output"]
