"""Tests for root and health check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root endpoint returns metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CogMesh Runtime Engine"
    assert data["status"] == "online"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Test /health endpoint returns database connectivity status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert "timestamp" in data
