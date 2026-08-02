"""Unit and integration tests for Capability Registry endpoints and CapabilityService."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_update_capability_success(client: AsyncClient) -> None:
    """Test reporting a capability snapshot for a registered device (create and upsert update)."""
    # 1. Register a device first
    reg_payload = {
        "device_name": "Node Beta",
        "device_type": "LAPTOP",
        "ip_address": "192.168.1.150",
        "port": 8000,
        "platform": "linux",
    }
    reg_res = await client.post("/api/v1/devices/register", json=reg_payload)
    assert reg_res.status_code == 201
    device_id = reg_res.json()["device_id"]

    # 2. Report Capability (Create)
    cap_payload = {
        "device_id": device_id,
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "battery_level": 90.0,
        "network_quality": "EXCELLENT",
        "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION"],
    }
    cap_res = await client.post("/api/v1/capabilities/report", json=cap_payload)
    assert cap_res.status_code == 200
    data = cap_res.json()
    assert data["device_id"] == device_id
    assert data["cpu_cores"] == 8
    assert data["ram_gb"] == 16.0
    assert data["battery_level"] == 90.0
    assert "OCR" in data["supported_tasks"]

    # 3. Report Capability again with updated values (Upsert Update)
    updated_payload = {
        "device_id": device_id,
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "battery_level": 75.0,  # Battery drained
        "network_quality": "GOOD",
        "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION", "MCQ_GEN"],
    }
    update_res = await client.post("/api/v1/capabilities/report", json=updated_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["battery_level"] == 75.0
    assert "MCQ_GEN" in updated_data["supported_tasks"]


@pytest.mark.asyncio
async def test_invalid_battery_validation_422(client: AsyncClient) -> None:
    """Test battery_level > 100 or < 0 returns HTTP 422 validation error."""
    device_id = str(uuid.uuid4())
    invalid_payload = {
        "device_id": device_id,
        "cpu_cores": 4,
        "ram_gb": 8.0,
        "battery_level": 150.0,  # Invalid battery percentage
        "supported_tasks": ["OCR"],
    }
    response = await client.post("/api/v1/capabilities/report", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_cpu_validation_422(client: AsyncClient) -> None:
    """Test cpu_cores <= 0 returns HTTP 422 validation error."""
    device_id = str(uuid.uuid4())
    invalid_payload = {
        "device_id": device_id,
        "cpu_cores": 0,  # Invalid CPU cores
        "ram_gb": 8.0,
        "battery_level": 80.0,
        "supported_tasks": ["OCR"],
    }
    response = await client.post("/api/v1/capabilities/report", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_ram_validation_422(client: AsyncClient) -> None:
    """Test ram_gb <= 0 returns HTTP 422 validation error."""
    device_id = str(uuid.uuid4())
    invalid_payload = {
        "device_id": device_id,
        "cpu_cores": 4,
        "ram_gb": 0.0,  # Invalid RAM
        "battery_level": 80.0,
        "supported_tasks": ["OCR"],
    }
    response = await client.post("/api/v1/capabilities/report", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_supported_tasks_validation_422(client: AsyncClient) -> None:
    """Test empty supported_tasks list returns HTTP 422 validation error."""
    device_id = str(uuid.uuid4())
    invalid_payload = {
        "device_id": device_id,
        "cpu_cores": 4,
        "ram_gb": 8.0,
        "battery_level": 80.0,
        "supported_tasks": [],  # Empty supported tasks list
    }
    response = await client.post("/api/v1/capabilities/report", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_unknown_device_report_404(client: AsyncClient) -> None:
    """Test reporting capability for an unregistered device_id returns HTTP 404 Not Found."""
    unknown_id = str(uuid.uuid4())
    payload = {
        "device_id": unknown_id,
        "cpu_cores": 4,
        "ram_gb": 8.0,
        "battery_level": 80.0,
        "supported_tasks": ["OCR"],
    }
    response = await client.post("/api/v1/capabilities/report", json=payload)
    assert response.status_code == 404
    assert response.json()["error"] == "DeviceNotFoundException"


@pytest.mark.asyncio
async def test_get_capability_by_device_id(client: AsyncClient) -> None:
    """Test retrieving single capability snapshot by device_id."""
    # 1. Register device
    reg_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Phone Gamma", "device_type": "PHONE", "ip_address": "10.0.0.20"
    })
    device_id = reg_res.json()["device_id"]

    # 2. Report Capability
    await client.post("/api/v1/capabilities/report", json={
        "device_id": device_id,
        "cpu_cores": 8,
        "ram_gb": 6.0,
        "battery_level": 100.0,
        "supported_tasks": ["TRANSLATION"],
    })

    # 3. GET /api/v1/capabilities/{device_id}
    get_res = await client.get(f"/api/v1/capabilities/{device_id}")
    assert get_res.status_code == 200
    assert get_res.json()["device_id"] == device_id
    assert get_res.json()["ram_gb"] == 6.0


@pytest.mark.asyncio
async def test_list_capabilities(client: AsyncClient) -> None:
    """Test listing all capability snapshots via GET /api/v1/capabilities."""
    response = await client.get("/api/v1/capabilities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
