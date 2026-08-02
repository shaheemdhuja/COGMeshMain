"""Central router registering all API V1 sub-routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    capabilities,
    communication,
    devices,
    goals,
    health,
    runtime,
    scheduler,
    workflows,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(devices.router)
api_router.include_router(capabilities.router)
api_router.include_router(goals.router)
api_router.include_router(workflows.router)
api_router.include_router(scheduler.router)
api_router.include_router(runtime.router)
api_router.include_router(communication.router)







