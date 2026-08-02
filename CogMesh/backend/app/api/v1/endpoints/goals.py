"""FastAPI REST API endpoints for Goal parsing and representation."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.structured_goal import StructuredGoal
from app.schemas.goal import GoalParseRequest
from app.services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post(
    "/parse",
    response_model=StructuredGoal,
    status_code=status.HTTP_200_OK,
    summary="Parse natural language goal into a StructuredGoal",
)
async def parse_goal(
    request: GoalParseRequest,
    db: AsyncSession = Depends(get_db),
) -> StructuredGoal:
    """Transform a natural language user request into an internal StructuredGoal object."""
    return await GoalService.parse_and_store_goal(db, request.goal, file_path=request.file_path)

