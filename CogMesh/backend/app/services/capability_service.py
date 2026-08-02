"""Capability Service managing capability registration, updates, and queries."""

from datetime import datetime, timezone
from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DeviceNotFoundException, EntityNotFoundException
from app.database.repository.capability_repository import CapabilityRepository
from app.database.repository.device_repository import DeviceRepository
from app.models.capability import Capability
from app.schemas.capability import CapabilityReport, CapabilityUpdate


class CapabilityService:
    """Service layer executing business logic for Capability Registry."""

    @staticmethod
    async def report_capability(db: AsyncSession, report: CapabilityReport) -> Capability:
        """Register or update (upsert) the capability snapshot for a device."""
        device_id_str = str(report.device_id)

        # 1. Validate device exists in registry
        device_repo = DeviceRepository(db)
        device = await device_repo.get_by_id(device_id_str)
        if not device:
            logger.warning(f"Capability Report rejected for unknown device_id: {device_id_str}")
            raise DeviceNotFoundException(device_id_str)

        # 2. Check if capability record exists
        cap_repo = CapabilityRepository(db)
        existing_cap = await cap_repo.get_by_device_id(device_id_str)

        now = datetime.now(timezone.utc)

        if existing_cap:
            existing_cap.cpu_cores = report.cpu_cores
            existing_cap.ram_gb = report.ram_gb
            existing_cap.battery_level = report.battery_level
            existing_cap.network_quality = report.network_quality
            existing_cap.supported_tasks = report.supported_tasks
            existing_cap.last_updated = now
            updated_cap = await cap_repo.update(existing_cap)
            logger.info(f"Capability updated for device {device_id_str}")
            return updated_cap

        # Create new capability snapshot
        new_cap = Capability(
            device_id=device_id_str,
            cpu_cores=report.cpu_cores,
            ram_gb=report.ram_gb,
            battery_level=report.battery_level,
            network_quality=report.network_quality,
            supported_tasks=report.supported_tasks,
            last_updated=now,
        )
        created_cap = await cap_repo.create(new_cap)
        logger.info(f"Capability registered for device {device_id_str}")
        return created_cap

    @staticmethod
    async def get_capability(db: AsyncSession, device_id: str) -> Capability:
        """Retrieve capability snapshot for a specific device UUID."""
        # Validate device existence
        device_repo = DeviceRepository(db)
        device = await device_repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundException(device_id)

        cap_repo = CapabilityRepository(db)
        capability = await cap_repo.get_by_device_id(device_id)
        if not capability:
            raise EntityNotFoundException("Capability", device_id)
        return capability

    @staticmethod
    async def get_all_capabilities(db: AsyncSession) -> List[Capability]:
        """Fetch all registered capability snapshots."""
        cap_repo = CapabilityRepository(db)
        return await cap_repo.get_all()

    @staticmethod
    async def update_capability(
        db: AsyncSession, device_id: str, update_data: CapabilityUpdate
    ) -> Capability:
        """Apply partial updates to a device's capability snapshot."""
        device_repo = DeviceRepository(db)
        device = await device_repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundException(device_id)

        cap_repo = CapabilityRepository(db)
        capability = await cap_repo.get_by_device_id(device_id)
        if not capability:
            raise EntityNotFoundException("Capability", device_id)

        if update_data.cpu_cores is not None:
            capability.cpu_cores = update_data.cpu_cores
        if update_data.ram_gb is not None:
            capability.ram_gb = update_data.ram_gb
        if update_data.battery_level is not None:
            capability.battery_level = update_data.battery_level
        if update_data.network_quality is not None:
            capability.network_quality = update_data.network_quality
        if update_data.supported_tasks is not None:
            capability.supported_tasks = update_data.supported_tasks

        capability.last_updated = datetime.now(timezone.utc)
        return await cap_repo.update(capability)
