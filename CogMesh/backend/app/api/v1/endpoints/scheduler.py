"""FastAPI REST API endpoints for Adaptive Task Scheduler execution planning."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.scheduler.planner import ExecutionPlan
from app.schemas.scheduler import SchedulerPlanRequest
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.post(
    "/plan",
    response_model=ExecutionPlan,
    status_code=status.HTTP_200_OK,
    summary="Generate ExecutionPlan mapping DAG tasks to optimal devices",
)
async def generate_plan(
    request: SchedulerPlanRequest,
    db: AsyncSession = Depends(get_db),
) -> ExecutionPlan:
    """Evaluate online edge nodes, compute weighted scores, and generate an ExecutionPlan for a goal."""
    return await SchedulerService.create_execution_plan(db, request.goal_id)


@router.get(
    "/{goal_id}",
    response_model=ExecutionPlan,
    status_code=status.HTTP_200_OK,
    summary="Retrieve generated ExecutionPlan for a goal",
)
async def get_plan(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExecutionPlan:
    """Retrieve the generated ExecutionPlan for a specific goal UUID."""
    return await SchedulerService.get_execution_plan(db, goal_id)
