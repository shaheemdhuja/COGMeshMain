"""Central router registering all API V1 sub-routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import devices, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(devices.router)

