"""TaskRegistry registering and looking up available AI task adapters."""

from typing import Any, Dict, List, Optional, Type
from loguru import logger

from app.tasks.base import BaseTaskAdapter
from app.workflow.enums import TaskType


class TaskRegistry:
    """Registry maintaining mappings from TaskTypes to concrete BaseTaskAdapter classes."""

    _registry: Dict[str, Type[BaseTaskAdapter]] = {}

    @classmethod
    def register(cls, task_type: str, adapter_cls: Type[BaseTaskAdapter]) -> None:
        """Register an adapter class for a given task type."""
        key = task_type.upper()
        cls._registry[key] = adapter_cls
        logger.info(f"[TaskRegistry] Registered adapter '{adapter_cls.__name__}' for task '{key}'")

    @classmethod
    def get_adapter_class(cls, task_type: str) -> Optional[Type[BaseTaskAdapter]]:
        """Lookup adapter class by task_type key."""
        return cls._registry.get(task_type.upper())

    @classmethod
    def get_supported_tasks(cls) -> List[str]:
        """Return list of all registered supported task types."""
        return list(cls._registry.keys())

    @classmethod
    def list_adapters(cls) -> List[Dict[str, Any]]:
        """Return metadata summaries of all registered task adapters."""
        adapters_info: List[Dict[str, Any]] = []
        for task_type, adapter_cls in cls._registry.items():
            instance = adapter_cls()
            adapters_info.append({
                "task_type": task_type,
                "adapter_name": instance.adapter_name,
                "provider_name": instance.provider_name,
                "model_name": instance.model_name,
                "supported_capabilities": instance.supported_capabilities(),
            })
        return adapters_info
