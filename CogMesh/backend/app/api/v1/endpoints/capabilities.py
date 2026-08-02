"""FastAPI REST API endpoints for Capability Registry operations."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.capability import CapabilityReport, CapabilityResponse
from app.services.capability_service import CapabilityService

router = APIRouter(prefix="/capabilities", tags=["Capabilities"])


@router.post(
    "/report",
    response_model=CapabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Report or update device capability snapshot",
)
async def report_capability(
    report_in: CapabilityReport,
    db: AsyncSession = Depends(get_db),
) -> CapabilityResponse:
    """Register or update the hardware/software capability snapshot for an edge device."""
    capability = await CapabilityService.report_capability(db, report_in)
    return CapabilityResponse.model_validate(capability)


@router.get(
    "",
    response_model=List[CapabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="List all device capabilities",
)
async def list_capabilities(
    db: AsyncSession = Depends(get_db),
) -> List[CapabilityResponse]:
    """Retrieve all capability snapshots currently registered in the runtime database."""
    capabilities = await CapabilityService.get_all_capabilities(db)
    return [CapabilityResponse.model_validate(c) for c in capabilities]


@router.get(
    "/{device_id}",
    response_model=CapabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get capability for a specific device",
)
async def get_capability(
    device_id: str,
    db: AsyncSession = Depends(get_db),
) -> CapabilityResponse:
    """Retrieve capability snapshot for a specific edge device by UUID."""
    capability = await CapabilityService.get_capability(db, device_id)
    return CapabilityResponse.model_validate(capability)
