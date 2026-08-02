"""Capability Repository providing specialized database operations for Capability entities."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.capability import Capability


class CapabilityRepository(BaseRepository[Capability]):
    """Specialized database repository for Capability records."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with Capability model."""
        super().__init__(Capability, db_session)

    async def get_by_device_id(self, device_id: str) -> Optional[Capability]:
        """Fetch latest capability snapshot for a specific device UUID."""
        stmt = select(Capability).where(Capability.device_id == device_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
