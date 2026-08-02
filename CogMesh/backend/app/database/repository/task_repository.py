"""Task Repository providing database operations for Task entities."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.task import Task


class TaskRepository(BaseRepository[Task]):
    """Specialized database repository for Task model persistence."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with Task model."""
        super().__init__(Task, db_session)

    async def get_by_workflow_id(self, workflow_id: str) -> List[Task]:
        """Fetch all task assignments for a specific workflow DAG UUID."""
        stmt = select(Task).where(Task.workflow_id == workflow_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
