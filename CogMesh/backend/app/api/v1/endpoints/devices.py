"""FastAPI REST API endpoints for Device registration, telemetry heartbeats, and status queries."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.device import DeviceCreate, DeviceResponse, HeartbeatRequest
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "/register",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new edge device",
)
async def register_device(
    device_in: DeviceCreate,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    """Register an edge device node in the CogMesh runtime registry."""
    device = await DeviceService.register_device(db, device_in)
    return DeviceResponse.model_validate(device)


@router.post(
    "/heartbeat",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit device heartbeat",
)
async def device_heartbeat(
    heartbeat_in: HeartbeatRequest,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    """Process heartbeat ping from registered edge node, updating last_seen and status."""
    device = await DeviceService.heartbeat(db, heartbeat_in)
    return DeviceResponse.model_validate(device)


@router.get(
    "",
    response_model=List[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="List all registered devices",
)
async def list_devices(
    db: AsyncSession = Depends(get_db),
) -> List[DeviceResponse]:
    """Retrieve all edge devices currently registered in the runtime database."""
    devices = await DeviceService.get_all_devices(db)
    return [DeviceResponse.model_validate(d) for d in devices]


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single device details",
)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    """Retrieve detailed information for a single edge device by UUID."""
    device = await DeviceService.get_device(db, device_id)
    return DeviceResponse.model_validate(device)
