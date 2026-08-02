"""Goal Repository providing database operations for Goal entities."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.goal import Goal


class GoalRepository(BaseRepository[Goal]):
    """Specialized database repository for Goal ORM model persistence."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with Goal model."""
        super().__init__(Goal, db_session)

    async def get_by_id(self, goal_id: str) -> Optional[Goal]:
        """Fetch goal record by primary key UUID string."""
        stmt = select(Goal).where(Goal.id == goal_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
