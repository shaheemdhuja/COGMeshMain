# CogMesh: Capability-Constrained Collaborative AI Runtime for Multi-Device Edge Intelligence

CogMesh is a modular, high-performance distributed edge AI runtime that coordinates heterogeneous devices (laptops, mobile phones, edge nodes) to execute complex, capability-constrained multi-stage AI workflows.

---

## 🏛 System Architecture

- **Backend**: Python 3.12, FastAPI, Async SQLAlchemy 2.0 (`sqlite+aiosqlite`), Loguru, Pydantic v2.
- **Persistence**: SQLite (Audit logs, workflow metadata, task status, devices, metrics).
- **Execution State**: Async In-Memory state management for real-time orchestration.

---

## 🔌 API Documentation — Device Management (Sprint 2)

### 1. Register Device
- **URL**: `POST /api/v1/devices/register`
- **Description**: Registers an edge node in the runtime database.
- **HTTP Success Code**: `201 Created`

#### Request Payload Example:
```json
{
  "device_name": "Master Laptop",
  "device_type": "LAPTOP",
  "ip_address": "192.168.1.50",
  "port": 8000,
  "platform": "windows"
}
```

#### Response Example (201 Created):
```json
{
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "device_name": "Master Laptop",
  "device_type": "LAPTOP",
  "ip_address": "192.168.1.50",
  "port": 8000,
  "platform": "windows",
  "status": "ONLINE",
  "registered_at": "2026-08-02T13:15:00Z",
  "last_seen": "2026-08-02T13:15:00Z"
}
```

#### Error Response (409 Conflict):
```json
{
  "error": "DeviceAlreadyRegisteredException",
  "message": "Device with ID '41f62aae-ae2b-46bd-a413-d27cfc1ce7ff' is already registered.",
  "details": {
    "entity": "Device",
    "id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff"
  }
}
```

---

### 2. Device Heartbeat
- **URL**: `POST /api/v1/devices/heartbeat`
- **Description**: Submits telemetry heartbeat updating node `last_seen` and operational `status`.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "status": "ONLINE"
}
```

#### Response Example (200 OK):
```json
{
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "device_name": "Master Laptop",
  "device_type": "LAPTOP",
  "ip_address": "192.168.1.50",
  "port": 8000,
  "platform": "windows",
  "status": "ONLINE",
  "registered_at": "2026-08-02T13:15:00Z",
  "last_seen": "2026-08-02T13:16:30Z"
}
```

---

### 3. List All Devices
- **URL**: `GET /api/v1/devices`
- **Description**: Retrieves all registered edge devices.
- **HTTP Success Code**: `200 OK`

#### Response Example (200 OK):
```json
[
  {
    "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
    "device_name": "Master Laptop",
    "device_type": "LAPTOP",
    "ip_address": "192.168.1.50",
    "port": 8000,
    "platform": "windows",
    "status": "ONLINE",
    "registered_at": "2026-08-02T13:15:00Z",
    "last_seen": "2026-08-02T13:16:30Z"
  },
  {
    "device_id": "d71aed75-50ea-4900-979e-e999566c04b1",
    "device_name": "Phone A",
    "device_type": "PHONE",
    "ip_address": "192.168.1.51",
    "port": 8000,
    "platform": "android",
    "status": "ONLINE",
    "registered_at": "2026-08-02T13:15:30Z",
    "last_seen": "2026-08-02T13:16:45Z"
  }
]
```

---

### 4. Get Single Device Details
- **URL**: `GET /api/v1/devices/{device_id}`
- **Description**: Retrieves single edge node by UUID.
- **HTTP Success Code**: `200 OK`

#### Response Example (200 OK):
```json
{
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "device_name": "Master Laptop",
  "device_type": "LAPTOP",
  "ip_address": "192.168.1.50",
  "port": 8000,
  "platform": "windows",
  "status": "ONLINE",
  "registered_at": "2026-08-02T13:15:00Z",
  "last_seen": "2026-08-02T13:16:30Z"
}
```

#### Error Response (404 Not Found):
```json
{
  "error": "DeviceNotFoundException",
  "message": "Device with ID 'non-existent-uuid' was not found.",
  "details": {
    "entity": "Device",
    "id": "non-existent-uuid"
  }
}
```

---

## 🧪 Running Tests

```bash
cd CogMesh/backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest
```