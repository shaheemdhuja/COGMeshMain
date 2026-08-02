"""FastAPI REST API endpoints for Mesh Communication Layer inspection."""

from typing import List
from fastapi import APIRouter, status

from app.communication.message import Connection, RuntimeMessage
from app.services.communication_service import CommunicationService

router = APIRouter(prefix="/communication", tags=["Mesh Communication"])


@router.get(
    "/connections",
    response_model=List[Connection],
    status_code=status.HTTP_200_OK,
    summary="List active Runtime Node connections",
)
async def list_connections() -> List[Connection]:
    """Retrieve all active or managed node connection sessions."""
    return CommunicationService.get_active_connections()


@router.get(
    "/messages",
    response_model=List[RuntimeMessage],
    status_code=status.HTTP_200_OK,
    summary="List recent transmitted RuntimeMessages",
)
async def list_messages() -> List[RuntimeMessage]:
    """Retrieve recent transmitted RuntimeMessage protocol audit logs."""
    return CommunicationService.get_recent_messages()
