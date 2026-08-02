"""FastAPI REST API endpoints for Capability-Constrained Execution DAG generation."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.workflow import WorkflowGenerateRequest
from app.services.workflow_service import WorkflowService
from app.workflow.dag import ExecutionDAG

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post(
    "/generate",
    response_model=ExecutionDAG,
    status_code=status.HTTP_200_OK,
    summary="Generate capability-constrained ExecutionDAG for a goal",
)
async def generate_workflow(
    request: WorkflowGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> ExecutionDAG:
    """Generate and optimize a capability-constrained ExecutionDAG for a goal."""
    return await WorkflowService.generate_workflow(db, request.goal_id)


@router.get(
    "/{goal_id}",
    response_model=ExecutionDAG,
    status_code=status.HTTP_200_OK,
    summary="Retrieve generated ExecutionDAG for a goal",
)
async def get_workflow(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExecutionDAG:
    """Retrieve the generated ExecutionDAG graph for a specific goal UUID."""
    return await WorkflowService.get_workflow(db, goal_id)
