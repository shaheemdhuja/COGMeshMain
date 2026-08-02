"""Workflow Repository for persisting generated Workflow DAG entities."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.workflow import Workflow


class WorkflowRepository(BaseRepository[Workflow]):
    """Specialized database repository for Workflow ORM model persistence."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with Workflow model."""
        super().__init__(Workflow, db_session)

    async def get_by_goal_id(self, goal_id: str) -> Optional[Workflow]:
        """Fetch latest workflow for a specific goal UUID."""
        stmt = select(Workflow).where(Workflow.goal_id == goal_id).order_by(Workflow.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()
