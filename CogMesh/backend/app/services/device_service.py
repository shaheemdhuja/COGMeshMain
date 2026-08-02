"""Device Service managing registration, heartbeats, status updates, and node queries."""

from datetime import datetime, timezone
from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DeviceAlreadyRegisteredException, DeviceNotFoundException
from app.database.repository.device_repository import DeviceRepository
from app.models.device import Device
from app.schemas.device import DeviceCreate, HeartbeatRequest


class DeviceService:
    """Service layer executing business logic for edge device management."""

    @staticmethod
    async def register_device(db: AsyncSession, device_in: DeviceCreate) -> Device:
        """Register a new edge device or raise 409 if device_id already exists."""
        repo = DeviceRepository(db)

        # Check if custom client device_id already exists
        if device_in.device_id:
            device_id_str = str(device_in.device_id)
            existing_device = await repo.get_by_id(device_id_str)
            if existing_device:
                logger.warning(f"Duplicate Registration attempt for device_id: {device_id_str}")
                raise DeviceAlreadyRegisteredException(device_id_str)

        # Instantiate Device ORM entity
        new_device = Device(
            device_name=device_in.device_name,
            device_type=device_in.device_type,
            ip_address=str(device_in.ip_address),
            port=device_in.port,
            platform=device_in.platform,
            status="ONLINE",
            last_seen=datetime.now(timezone.utc),
        )

        if device_in.device_id:
            new_device.id = str(device_in.device_id)

        created_device = await repo.create(new_device)
        logger.info(f"Device Registered: {created_device.id} ({created_device.device_name})")
        return created_device

    @staticmethod
    async def heartbeat(db: AsyncSession, heartbeat_in: HeartbeatRequest) -> Device:
        """Process heartbeat signal from an active device and update last_seen/status."""
        repo = DeviceRepository(db)
        device_id_str = str(heartbeat_in.device_id)

        updated_device = await repo.update_heartbeat(
            device_id=device_id_str,
            status=heartbeat_in.status,
            last_seen=datetime.now(timezone.utc),
        )

        if not updated_device:
            logger.warning(f"Heartbeat Received for unregistered device_id: {device_id_str}")
            raise DeviceNotFoundException(device_id_str)

        logger.info(f"Heartbeat Received from device {device_id_str} (status: {updated_device.status})")
        return updated_device

    @staticmethod
    async def get_device(db: AsyncSession, device_id: str) -> Device:
        """Retrieve a specific registered device by ID or raise 404."""
        repo = DeviceRepository(db)
        device = await repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundException(device_id)
        return device

    @staticmethod
    async def get_all_devices(db: AsyncSession) -> List[Device]:
        """Fetch a list of all registered edge devices."""
        repo = DeviceRepository(db)
        return await repo.get_all()

    @staticmethod
    async def update_status(db: AsyncSession, device_id: str, status: str) -> Device:
        """Update operational status of a specific device."""
        repo = DeviceRepository(db)
        device = await repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundException(device_id)

        device.status = status
        return await repo.update(device)
