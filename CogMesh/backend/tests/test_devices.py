"""Unit and integration tests for Device Management API endpoints and DeviceService."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_device_success(client: AsyncClient) -> None:
    """Test registering a new device with valid payload returns HTTP 201."""
    payload = {
        "device_name": "Laptop Alpha",
        "device_type": "LAPTOP",
        "ip_address": "192.168.1.100",
        "port": 8000,
        "platform": "windows",
    }
    response = await client.post("/api/v1/devices/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "device_id" in data
    assert data["device_name"] == "Laptop Alpha"
    assert data["device_type"] == "LAPTOP"
    assert data["ip_address"] == "192.168.1.100"
    assert data["platform"] == "windows"
    assert data["status"] == "ONLINE"


@pytest.mark.asyncio
async def test_register_device_duplicate_409(client: AsyncClient) -> None:
    """Test registering a device with an existing device_id returns HTTP 409 Conflict."""
    custom_id = str(uuid.uuid4())
    payload = {
        "device_id": custom_id,
        "device_name": "Phone One",
        "device_type": "PHONE",
        "ip_address": "192.168.1.101",
        "port": 8000,
        "platform": "android",
    }

    # First registration
    res1 = await client.post("/api/v1/devices/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same custom_id
    res2 = await client.post("/api/v1/devices/register", json=payload)
    assert res2.status_code == 409
    err_data = res2.json()
    assert err_data["error"] == "DeviceAlreadyRegisteredException"


@pytest.mark.asyncio
async def test_register_device_invalid_ip_422(client: AsyncClient) -> None:
    """Test registering with an invalid IP address format returns HTTP 422."""
    payload = {
        "device_name": "Invalid Node",
        "device_type": "PHONE",
        "ip_address": "not-an-ip-address",
        "port": 8000,
    }
    response = await client.post("/api/v1/devices/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_device_heartbeat_success(client: AsyncClient) -> None:
    """Test sending heartbeat for a registered device returns HTTP 200."""
    # 1. Register device
    reg_payload = {
        "device_name": "Tablet Edge",
        "device_type": "TABLET",
        "ip_address": "192.168.1.102",
        "port": 8080,
        "platform": "ios",
    }
    reg_res = await client.post("/api/v1/devices/register", json=reg_payload)
    assert reg_res.status_code == 201
    device_id = reg_res.json()["device_id"]

    # 2. Send heartbeat
    hb_payload = {
        "device_id": device_id,
        "status": "ONLINE",
    }
    hb_res = await client.post("/api/v1/devices/heartbeat", json=hb_payload)
    assert hb_res.status_code == 200
    hb_data = hb_res.json()
    assert hb_data["device_id"] == device_id
    assert hb_data["status"] == "ONLINE"


@pytest.mark.asyncio
async def test_device_heartbeat_not_found_404(client: AsyncClient) -> None:
    """Test sending heartbeat for a non-existent device returns HTTP 404 Not Found."""
    fake_id = str(uuid.uuid4())
    hb_payload = {
        "device_id": fake_id,
        "status": "ONLINE",
    }
    response = await client.post("/api/v1/devices/heartbeat", json=hb_payload)
    assert response.status_code == 404
    assert response.json()["error"] == "DeviceNotFoundException"


@pytest.mark.asyncio
async def test_list_devices(client: AsyncClient) -> None:
    """Test GET /api/v1/devices returns list of all registered devices."""
    # Register 2 devices
    await client.post("/api/v1/devices/register", json={
        "device_name": "Dev A", "device_type": "LAPTOP", "ip_address": "10.0.0.1"
    })
    await client.post("/api/v1/devices/register", json={
        "device_name": "Dev B", "device_type": "PHONE", "ip_address": "10.0.0.2"
    })

    response = await client.get("/api/v1/devices")
    assert response.status_code == 200
    devices_list = response.json()
    assert len(devices_list) >= 2


@pytest.mark.asyncio
async def test_get_device_by_id(client: AsyncClient) -> None:
    """Test GET /api/v1/devices/{device_id} for existing and missing devices."""
    reg_res = await client.post("/api/v1/devices/register", json={
        "device_name": "Node X", "device_type": "SERVER", "ip_address": "10.0.0.5"
    })
    device_id = reg_res.json()["device_id"]

    # Success case
    res_ok = await client.get(f"/api/v1/devices/{device_id}")
    assert res_ok.status_code == 200
    assert res_ok.json()["device_name"] == "Node X"

    # Missing case
    fake_id = str(uuid.uuid4())
    res_404 = await client.get(f"/api/v1/devices/{fake_id}")
    assert res_404.status_code == 404
    assert res_404.json()["error"] == "DeviceNotFoundException"
