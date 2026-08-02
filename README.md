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

## 🔀 API Documentation — Workflow Generator (Sprint 5)

### 1. Generate Capability-Constrained ExecutionDAG
- **URL**: `POST /api/v1/workflows/generate`
- **Description**: Validates capability constraints across active mesh nodes, generates an `ExecutionDAG`, optimizes the DAG (duplicate node removal, edge compaction), and persists the workflow definition in SQLite.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

#### Response Example (200 OK - ExecutionDAG JSON):
```json
{
  "dag_id": "e4a77b81-2299-4c54-8e10-c44d71239999",
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "nodes": {
    "node-uuid-1": {
      "node_id": "node-uuid-1",
      "task_type": "OCR",
      "dependencies": [],
      "required_capabilities": ["OCR"],
      "status": "PENDING",
      "estimated_cost": 1.0,
      "metadata": { "original_operation": "OCR" }
    },
    "node-uuid-2": {
      "node_id": "node-uuid-2",
      "task_type": "SUMMARIZATION",
      "dependencies": ["node-uuid-1"],
      "required_capabilities": ["SUMMARIZATION"],
      "status": "PENDING",
      "estimated_cost": 1.0,
      "metadata": { "original_operation": "SUMMARIZATION" }
    }
  },
  "edges": [
    {
      "edge_id": "edge-uuid-1",
      "source": "node-uuid-1",
      "destination": "node-uuid-2"
    }
  ]
}
```

#### Error Response (409 Conflict - Missing Capability Constraint Violation):
```json
{
  "error": "MissingCapabilityException",
  "message": "Workflow generation failed: required capability 'SUMMARIZATION' is not supported by any active device in the mesh.",
  "details": {
    "missing_capability": "SUMMARIZATION"
  }
}
```

---

### 2. Retrieve Generated Workflow
- **URL**: `GET /api/v1/workflows/{goal_id}`
- **Description**: Retrieves the generated `ExecutionDAG` graph for a specific goal UUID.
- **HTTP Success Code**: `200 OK`

---

## ⚙️ Workflow Subsystem Architecture (`app/workflow/`)

```
backend/app/workflow/
├── enums.py         # TaskType, NodeStatus, WorkflowStatus
├── node.py          # ExecutionNode (task_type, dependencies, required_capabilities)
├── edge.py          # ExecutionEdge (source -> destination dependency link)
├── dag.py           # ExecutionDAG graph (add_node, add_edge, validate, topological_sort)
├── generator.py     # WorkflowGenerator (capability constraint validation & graph creation)
└── optimizer.py     # WorkflowOptimizer (consecutive duplicate node removal & edge compaction)
```

> [!IMPORTANT]
> **Device Independence**: The `WorkflowGenerator` subsystem validates capability requirements against active mesh capability snapshots but **NEVER** interacts with devices, assigns nodes, or performs scheduling. The generated `ExecutionDAG` is passed to the Scheduler in downstream sprints.

---

## 🗓️ API Documentation — Adaptive Task Scheduler (Sprint 6)

### 1. Generate ExecutionPlan
- **URL**: `POST /api/v1/scheduler/plan`
- **Description**: Evaluates online edge nodes, computes weighted scoring metrics (`SchedulingScore`), binds each `ExecutionNode` in topological order to an optimal edge device, persists scheduled tasks in SQLite, and returns an `ExecutionPlan`.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

#### Response Example (200 OK - ExecutionPlan JSON):
```json
{
  "plan_id": "a5d88921-1123-4567-8901-abcdef123456",
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "workflow_id": "e4a77b81-2299-4c54-8e10-c44d71239999",
  "assignments": [
    {
      "assignment_id": "b1111111-2222-3333-4444-555555555555",
      "node_id": "node-uuid-1",
      "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
      "task_type": "OCR",
      "priority": 1,
      "reason": "Assigned to Master Laptop (41f62aae...) - Selected with weighted score 0.970 (Battery: 95%, RAM: 32GB, CPU: 16 cores, Network: EXCELLENT)",
      "estimated_duration": 2.0
    },
    {
      "assignment_id": "c2222222-3333-4444-5555-666666666666",
      "node_id": "node-uuid-2",
      "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
      "task_type": "SUMMARIZATION",
      "priority": 1,
      "reason": "Assigned to Master Laptop (41f62aae...) - Selected with weighted score 0.970 (Battery: 95%, RAM: 32GB, CPU: 16 cores, Network: EXCELLENT)",
      "estimated_duration": 2.0
    }
  ],
  "created_at": "2026-08-02T13:50:00Z"
}
```

#### Error Response (409 Conflict - No Eligible Device Available):
```json
{
  "error": "NoEligibleDeviceException",
  "message": "Scheduling failed: no online and capable device available to execute task 'SUMMARIZATION'.",
  "details": {
    "task_type": "SUMMARIZATION"
  }
}
```

---

### 2. Retrieve Generated ExecutionPlan
- **URL**: `GET /api/v1/scheduler/{goal_id}`
- **Description**: Retrieves the generated `ExecutionPlan` for a specific goal UUID.
- **HTTP Success Code**: `200 OK`

---

## 🧮 Weighted Scoring Formula (`app/scheduler/scoring.py`)

The `AdaptiveScheduler` ranks candidate edge nodes using a deterministic weighted scoring system:

$$\text{Score} = (0.35 \times C) + (0.20 \times B) + (0.20 \times R) + (0.15 \times P) + (0.10 \times N)$$

- $C$ (**Capability Match**): `1.0` if all required task capabilities are supported, else `0.0` (Hard Rejection).
- $B$ (**Battery Level**): $\frac{\text{battery\_level}}{100.0}$ (Normalized $[0.0, 1.0]$).
- $R$ (**RAM GB**): $\min\left(\frac{\text{ram\_gb}}{32.0}, 1.0\right)$ (Normalized against 32GB baseline).
- $P$ (**CPU Cores**): $\min\left(\frac{\text{cpu\_cores}}{16.0}, 1.0\right)$ (Normalized against 16 cores baseline).
- $N$ (**Network Quality**): `1.0` (EXCELLENT), `0.8` (GOOD), `0.5` (FAIR), `0.2` (POOR).

---

## ⚡ API Documentation — Runtime Orchestrator (Sprint 7)

### 1. Dispatch ExecutionPlan Execution
- **URL**: `POST /api/v1/runtime/start`
- **Description**: Dispatches an `ExecutionPlan` through the `RuntimeOrchestrator`, enqueuing task assignments in an in-memory `ExecutionQueue` (FIFO), executing simulated task inference using `FakeExecutor`, emitting `RuntimeEvents`, and persisting logs (`TaskLog`) and metrics (`ExecutionMetric`) in SQLite.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

#### Response Example (200 OK - ExecutionContext JSON):
```json
{
  "context_id": "f8123456-7890-abcd-ef12-34567890abcd",
  "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "COMPLETED",
  "task_states": {
    "node-uuid-1": "COMPLETED",
    "node-uuid-2": "COMPLETED"
  },
  "results": {
    "node-uuid-1": {
      "text": "Simulated extracted text from lecture document...",
      "confidence": 0.98
    },
    "node-uuid-2": {
      "summary": "Simulated summary of lecture text..."
    }
  },
  "metrics": {
    "node-uuid-1": {
      "execution_time_ms": 52.4,
      "cpu_usage_percent": 35.5,
      "ram_usage_mb": 128.0,
      "energy_cost_joules": 4.2
    }
  },
  "events": [
    {
      "event_id": "evt-1",
      "event_type": "PLAN_STARTED",
      "context_id": "f8123456-7890-abcd-ef12-34567890abcd",
      "goal_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "message": "Execution plan 'plan-uuid' started with 2 task assignments.",
      "timestamp": "2026-08-02T13:55:00Z"
    },
    {
      "event_id": "evt-2",
      "event_type": "TASK_READY",
      "node_id": "node-uuid-1",
      "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
      "message": "Task 'OCR' (node-uuid-1) is READY for device '41f62aae...'.",
      "timestamp": "2026-08-02T13:55:00Z"
    },
    {
      "event_id": "evt-3",
      "event_type": "TASK_STARTED",
      "node_id": "node-uuid-1",
      "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
      "message": "Task 'OCR' (node-uuid-1) started on device '41f62aae...'.",
      "timestamp": "2026-08-02T13:55:00Z"
    },
    {
      "event_id": "evt-4",
      "event_type": "TASK_COMPLETED",
      "node_id": "node-uuid-1",
      "device_id": "41f62aae-ae2b-46bd-a413-d27cfc1ce7ff",
      "message": "Task 'OCR' (node-uuid-1) COMPLETED successfully.",
      "timestamp": "2026-08-02T13:55:01Z"
    },
    {
      "event_id": "evt-5",
      "event_type": "PLAN_COMPLETED",
      "message": "Execution plan 'plan-uuid' completed successfully.",
      "timestamp": "2026-08-02T13:55:02Z"
    }
  ]
}
```

---

### 2. Get Real-Time Runtime Status
- **URL**: `GET /api/v1/runtime/status/{context_id}`
- **Description**: Retrieves in-memory `ExecutionContext` by UUID.
- **HTTP Success Code**: `200 OK`

---

### 3. Cancel Active Execution Context
- **URL**: `POST /api/v1/runtime/cancel/{context_id}`
- **Description**: Aborts execution for an active context and marks non-terminal tasks as `CANCELLED`.
- **HTTP Success Code**: `200 OK`

---

## 🔄 Task State Machine Lifecycle

```
    [ PENDING ]
         |
         +--------------------> [ CANCELLED ] (Terminal)
         |                           ^
         v                           |
     [ READY ] ----------------------+
         |                           |
         v                           |
    [ RUNNING ] ---------------------+
         |
         +--------------------> [ FAILED ]    (Terminal)
         |
         v
    [ COMPLETED ]                             (Terminal)
```

---

## 📡 API Documentation — Mesh Communication Layer (Sprint 8)

### 1. List Active Runtime Node Connections
- **URL**: `GET /api/v1/communication/connections`
- **Description**: Retrieves all active or managed `Connection` objects tracked by the `ConnectionManager`.
- **HTTP Success Code**: `200 OK`

#### Response Example (200 OK):
```json
[
  {
    "connection_id": "conn-uuid-1",
    "node_id": "device-uuid-100",
    "status": "CONNECTED",
    "last_seen": "2026-08-02T14:05:00Z",
    "transport": "WEBSOCKET"
  }
]
```

---

### 2. List Recent Transmitted RuntimeMessages
- **URL**: `GET /api/v1/communication/messages`
- **Description**: Retrieves recent `RuntimeMessage` protocol audit logs transmitted across the transport adapter.
- **HTTP Success Code**: `200 OK`

#### Response Example (200 OK):
```json
[
  {
    "message_id": "msg-uuid-1",
    "message_type": "TASK_ASSIGNMENT",
    "source_node": "ORCHESTRATOR",
    "destination_node": "device-uuid-100",
    "timestamp": "2026-08-02T14:05:01Z",
    "payload": {
      "task_id": "node-uuid-1",
      "task_type": "OCR"
    }
  }
]
```

---

## 🏗️ Transport Abstraction Architecture (`app/communication/`)

```
+-------------------------------------------------------------------------------+
|                             RuntimeOrchestrator                               |
+-------------------------------------------------------------------------------+
                                        |
                                        v  (Depends ONLY on Abstract Transport Interface)
+-------------------------------------------------------------------------------+
|                              Transport Interface                              |
|   connect() | disconnect() | send() | broadcast() | receive()                 |
+-------------------------------------------------------------------------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
+------------------------------------+    +------------------------------------+
|          WebSocketAdapter          |    |        (Future Adapters)           |
| (Manages websockets & message log) |    |   (gRPC, HTTP Long Polling, etc.)  |
+------------------------------------+    +------------------------------------+
                   |
                   v
+-------------------------------------------------------------------------------+
|                              ConnectionManager                                |
|           (Tracks active nodes, session freshness & last_seen)                 |
+-------------------------------------------------------------------------------+
```

---

## 🤖 API Documentation — AI Task Adapter Layer (Sprint 9)

### 1. List Registered Task Adapters
- **URL**: `GET /api/v1/tasks`
- **Description**: Retrieves metadata summaries for all registered AI task adapters.
- **HTTP Success Code**: `200 OK`

#### Response Example (200 OK):
```json
[
  {
    "task_type": "OCR",
    "adapter_name": "OCRAdapter",
    "provider_name": "MockOCRProvider",
    "model_name": "mock-tesseract-v5",
    "supported_capabilities": ["OCR"]
  },
  {
    "task_type": "SUMMARIZATION",
    "adapter_name": "SummaryAdapter",
    "provider_name": "MockGemmaProvider",
    "model_name": "mock-gemma-2b",
    "supported_capabilities": ["SUMMARIZATION"]
  }
]
```

---

### 2. Execute Task via Adapter Layer
- **URL**: `POST /api/v1/tasks/execute`
- **Description**: Executes an AI task through `TaskRegistry` $\rightarrow$ `AdapterFactory` $\rightarrow$ `BaseTaskAdapter`, records an audit entry in SQLite (`task_execution_audits`), and returns a `TaskResult`.
- **HTTP Success Code**: `200 OK`

#### Request Payload Example:
```json
{
  "task_type": "OCR",
  "input_data": {
    "page": 1,
    "language": "English"
  }
}
```

#### Response Example (200 OK - TaskResult JSON):
```json
{
  "task_id": "res-uuid-100",
  "status": "SUCCESS",
  "output": {
    "text": "Extracted lecture notes: CogMesh architecture enables distributed edge intelligence...",
    "confidence": 0.985,
    "word_count": 13,
    "page_number": 1
  },
  "execution_time_ms": 20.4,
  "adapter_name": "OCRAdapter",
  "provider_name": "MockOCRProvider",
  "model_name": "mock-tesseract-v5",
  "metadata": {
    "simulated": true
  }
}
```

---

## 🧩 Task Adapter Layer Architecture (`app/tasks/`)

```
+-------------------------------------------------------------------------------+
|                             RuntimeOrchestrator                               |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                                 TaskRegistry                                  |
|                 (Maintains TaskType -> AdapterClass mappings)                |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                                AdapterFactory                                 |
|                     (Instantiates BaseTaskAdapter subclass)                   |
+-------------------------------------------------------------------------------+
                                        |
         +------------------------------+------------------------------+
         |                              |                              |
         v                              v                              v
+------------------+          +------------------+          +------------------+
|    OCRAdapter    |          |  SummaryAdapter  |          |   MCQAdapter     |
| (MockOCRProvider)|          | (MockGemmaProvid)|          | (MockLlamaProvid)|
+------------------+          +------------------+          +------------------+
         |                              |                              |
         v                              v                              v
  [ AI Model Engine ]            [ AI Model Engine ]            [ AI Model Engine ]
```

---

## ⚡ Real AI Providers Integration — Milestone 10A

Milestone 10A integrates real AI provider wrappers (`TesseractProvider`, `OllamaProvider`, `TranslationProvider`) behind the `BaseTaskAdapter` interface without modifying the frozen architecture.

```
+-------------------------------------------------------------------------------+
|                             RuntimeOrchestrator                               |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                                 TaskRegistry                                  |
|                 (Maintains TaskType -> AdapterClass mappings)                |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                                AdapterFactory                                 |
|                     (Instantiates BaseTaskAdapter subclass)                   |
+-------------------------------------------------------------------------------+
                                        |
         +------------------------------+------------------------------+
         |                              |                              |
         v                              v                              v
+------------------+          +------------------+          +------------------+
|    OCRAdapter    |          |  SummaryAdapter  |          |   MCQAdapter     |
|(TesseractProvide)|          | (OllamaProvider) |          | (OllamaProvider) |
+------------------+          +------------------+          +------------------+
         |                              |                              |
         v                              v                              v
  [ Tesseract Binary ]         [ Local Ollama HTTP API ]      [ Local Ollama HTTP API ]
```

### Environment Configuration (`.env`)

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:latest
TESSERACT_PATH=tesseract
TRANSLATION_PROVIDER=ollama
```

---

## 🌐 Real Multi-Device Execution — Milestone 10C

Milestone 10C enables real WebSocket-based communication between the CogMesh Master Server and remote edge devices (laptops, mobile phones, Raspberry Pis).

```
RuntimeOrchestrator
        │
        ▼
Communication Layer (/api/v1/communication/ws/node/{device_id})
        │
        ▼
WebSocket Transport
        │
        ▼
Remote Edge Client (scripts/edge_node_client.py)
        │
        ▼
AdapterFactory ──> BaseTaskAdapter ──> Provider ──> TaskResult
```

### Running a Remote Edge Client Node

On any secondary laptop or edge device:

```powershell
cd CogMesh/backend
.\venv\Scripts\python.exe scripts/edge_node_client.py --server-url ws://<MASTER_SERVER_IP>:8000 --device-id edge-node-02 --device-name "Secondary Laptop Edge Node"
```

---

## 🧪 Running Tests

```bash
cd CogMesh/backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest
```