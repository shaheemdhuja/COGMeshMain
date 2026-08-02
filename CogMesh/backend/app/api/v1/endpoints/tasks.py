"""FastAPI REST API endpoints for AI Task Adapter Layer execution and inspection."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.tasks import TaskAdapterResponse, TaskExecuteRequest
from app.services.task_service import TaskService
from app.tasks.result import TaskResult

router = APIRouter(prefix="/tasks", tags=["AI Task Adapters"])


@router.get(
    "",
    response_model=List[TaskAdapterResponse],
    status_code=status.HTTP_200_OK,
    summary="List registered AI task adapters and provider metadata",
)
async def list_adapters() -> List[TaskAdapterResponse]:
    """Retrieve metadata for all registered AI task adapters."""
    return TaskService.list_adapters()


@router.post(
    "/execute",
    response_model=TaskResult,
    status_code=status.HTTP_200_OK,
    summary="Execute an AI task through the adapter layer",
)
async def execute_task(
    request: TaskExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> TaskResult:
    """Execute specified AI task using AdapterFactory and return TaskResult."""
    return await TaskService.execute_task(db, request.task_type, request.input_data)
