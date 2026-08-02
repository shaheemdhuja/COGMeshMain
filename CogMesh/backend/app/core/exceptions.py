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


class WorkflowException(CogMeshException):
    """Raised when workflow generation or execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize workflow exception."""
        super().__init__(message, status_code=400, details=details)
