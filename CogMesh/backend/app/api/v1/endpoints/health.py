"""Health check endpoint implementation."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Check application health status")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check health status of the API service and its database connectivity."""
    db_connected = False
    try:
        result = await db.execute(text("SELECT 1"))
        db_connected = result.scalar() == 1
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        project_name=settings.PROJECT_NAME,
        database_connected=db_connected,
        timestamp=datetime.now(timezone.utc),
    )
