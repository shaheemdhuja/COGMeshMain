"""FastAPI REST API endpoints for Runtime Orchestrator execution dispatch and context monitoring."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.execution_context import ExecutionContext
from app.schemas.runtime import RuntimeStartRequest
from app.services.runtime_service import RuntimeService

router = APIRouter(prefix="/runtime", tags=["Runtime Orchestrator"])


@router.post(
    "/start",
    response_model=ExecutionContext,
    status_code=status.HTTP_200_OK,
    summary="Dispatch ExecutionPlan execution through RuntimeOrchestrator",
)
async def start_execution(
    request: RuntimeStartRequest,
    db: AsyncSession = Depends(get_db),
) -> ExecutionContext:
    """Execute scheduled tasks for a goal using FakeExecutor and emit runtime events."""
    return await RuntimeService.start_execution(db, request.goal_id)


@router.get(
    "/status/{context_id}",
    response_model=ExecutionContext,
    status_code=status.HTTP_200_OK,
    summary="Get real-time execution context status and event log",
)
async def get_runtime_status(context_id: str) -> ExecutionContext:
    """Retrieve in-memory ExecutionContext details by context UUID."""
    return RuntimeService.get_runtime_status(context_id)


@router.post(
    "/cancel/{context_id}",
    response_model=ExecutionContext,
    status_code=status.HTTP_200_OK,
    summary="Cancel active runtime execution context",
)
async def cancel_execution(context_id: str) -> ExecutionContext:
    """Abort an active execution context and mark pending tasks as CANCELLED."""
    return RuntimeService.cancel_execution(context_id)
