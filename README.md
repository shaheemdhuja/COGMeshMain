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

## ⚡ API Documentation — Capability Registry (Sprint 3)

### 1. Report / Update Device Capability
- **URL**: `POST /api/v1/capabilities/report`
- **Description**: Registers or updates (upserts) the latest hardware and AI execution capability snapshot for an edge device.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "cpu_cores": 8,
  "ram_gb": 16.0,
  "battery_level": 85.5,
  "network_quality": "EXCELLENT",
  "supported_tasks": ["OCR", "SUMMARIZATION", "TRANSLATION"]
}
```

#### Response Example (200 OK):
```json
{
  "id": "e982173a-44ba-432d-8b01-526487e41123",
  "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
  "cpu_cores": 8,
  "ram_gb": 16.0,
  "battery_level": 85.5,
  "network_quality": "EXCELLENT",
  "supported_tasks": [
    "OCR",
    "SUMMARIZATION",
    "TRANSLATION"
  ],
  "last_updated": "2026-08-02T13:20:00Z"
}
```

#### Error Response (404 Not Found - Unknown Device):
```json
{
  "error": "DeviceNotFoundException",
  "message": "Device with ID 'unregistered-uuid' was not found.",
  "details": {
    "entity": "Device",
    "id": "unregistered-uuid"
  }
}
```

#### Error Response (422 Unprocessable Entity - Validation Failure):
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "battery_level"],
      "msg": "Input should be less than or equal to 100",
      "input": 150.0
    }
  ]
}
```

---

### 2. Get Single Device Capability
- **URL**: `GET /api/v1/capabilities/{device_id}`
- **Description**: Retrieves capability snapshot for a specific edge device by UUID.
- **HTTP Success Code**: `200 OK`

---

### 3. List All Capabilities
- **URL**: `GET /api/v1/capabilities`
- **Description**: Retrieves capability snapshots across all registered edge nodes.
- **HTTP Success Code**: `200 OK`

---

## 🎯 API Documentation — Goal Service (Sprint 4)

### 1. Parse Natural Language Goal
- **URL**: `POST /api/v1/goals/parse`
- **Description**: Transforms a user's natural language goal input into an internal `StructuredGoal` domain object.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "goal": "Summarize this lecture PDF and generate MCQs."
}
```

#### Response Example (200 OK - StructuredGoal JSON):
```json
{
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "natural_language_input": "Summarize this lecture PDF and generate MCQs.",
  "goal_type": "lecture_processing",
  "input_type": "pdf",
  "operations": [
    "OCR",
    "SUMMARIZATION",
    "MCQ_GENERATION"
  ],
  "priority": 1,
  "constraints": {},
  "metadata": {
    "parsed_at": "2026-08-02T13:30:00Z",
    "parser_strategy": "deterministic_rule_based"
  }
}
```

#### Error Response (422 Unprocessable Entity - Parsing Failure):
```json
{
  "error": "GoalParsingException",
  "message": "Unable to identify any supported AI operations from input.",
  "details": {
    "input": "unrecognized input text"
  }
}
```

---

## 🧠 Domain Layer Architecture (`app/domain/`)

- **`StructuredGoal`**: Internal representation of parsed user intent (decoupled from raw text and downstream scheduling/workflows).
- **`ExecutionContext`**: Central in-memory runtime container encapsulating goal parameters, DAG workflows, device registries, capability maps, active task state machines, intermediate results, and telemetry metrics.

---

## 🧪 Running Tests

```bash
cd CogMesh/backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest
```