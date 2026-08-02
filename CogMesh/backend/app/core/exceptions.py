"""Custom domain and application exception definitions for CogMesh."""

from typing import Any, Dict, Optional


class CogMeshException(Exception):
    """Base exception class for all CogMesh runtime errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize base exception with message, HTTP status code, and optional details."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(CogMeshException):
    """Raised when a requested resource/entity is not found."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        """Initialize entity not found exception."""
        message = f"{entity_name} with ID '{entity_id}' was not found."
        super().__init__(message, status_code=404, details={"entity": entity_name, "id": entity_id})


class DuplicateEntityException(CogMeshException):
    """Raised when attempting to register or create an entity that already exists."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        """Initialize duplicate entity exception."""
        message = f"{entity_name} with ID '{entity_id}' is already registered."
        super().__init__(message, status_code=409, details={"entity": entity_name, "id": entity_id})


class DatabaseException(CogMeshException):
    """Raised when a database interaction fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize database exception."""
        super().__init__(message, status_code=500, details=details)


class DeviceNotFoundException(EntityNotFoundException):
    """Raised when a specific device cannot be located in runtime registry or DB."""

    def __init__(self, device_id: str) -> None:
        """Initialize device not found exception."""
        super().__init__("Device", device_id)


class DeviceAlreadyRegisteredException(DuplicateEntityException):
    """Raised when registering a device ID that already exists in the system."""

    def __init__(self, device_id: str) -> None:
        """Initialize device already registered exception."""
        super().__init__("Device", device_id)


class GoalNotFoundException(EntityNotFoundException):
    """Raised when a requested goal is missing."""

    def __init__(self, goal_id: str) -> None:
        """Initialize goal not found exception."""
        super().__init__("Goal", goal_id)


class GoalParsingException(CogMeshException):
    """Raised when a natural language goal string cannot be parsed into a StructuredGoal."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize goal parsing exception."""
        super().__init__(message, status_code=422, details=details)


class WorkflowException(CogMeshException):
    """Raised when workflow generation or execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize workflow exception."""
        super().__init__(message, status_code=400, details=details)


class MissingCapabilityException(CogMeshException):
    """Raised when workflow generation fails due to missing capability constraint in the mesh."""

    def __init__(self, missing_capability: str) -> None:
        """Initialize missing capability exception."""
        message = f"Workflow generation failed: required capability '{missing_capability}' is not supported by any active device in the mesh."
        super().__init__(message, status_code=409, details={"missing_capability": missing_capability})


class NoEligibleDeviceException(CogMeshException):
    """Raised when the scheduler cannot find any online or capable device for a specific task node."""

    def __init__(self, task_type: str) -> None:
        """Initialize no eligible device exception."""
        message = f"Scheduling failed: no online and capable device available to execute task '{task_type}'."
        super().__init__(message, status_code=409, details={"task_type": task_type})



