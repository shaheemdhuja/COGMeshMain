"""Device repository providing specialized data access operations for Device entities."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.device import Device


class DeviceRepository(BaseRepository[Device]):
    """Specialized database repository for Device operations."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with Device model."""
        super().__init__(Device, db_session)

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """Fetch device by UUID string."""
        stmt = select(Device).where(Device.id == device_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_heartbeat(
        self, device_id: str, status: str, last_seen: Optional[datetime] = None
    ) -> Optional[Device]:
        """Update last_seen timestamp and status for an existing device."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        device.last_seen = last_seen or datetime.now(timezone.utc)
        device.status = status
        await self.session.flush()
        await self.session.refresh(device)
        return device
