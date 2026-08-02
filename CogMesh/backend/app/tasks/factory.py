"""AdapterFactory instantiating task adapters from TaskRegistry."""

from app.core.exceptions import WorkflowException
from app.tasks.base import BaseTaskAdapter
from app.tasks.registry import TaskRegistry


class AdapterFactory:
    """Factory instantiating concrete BaseTaskAdapter objects for specified task types."""

    @classmethod
    def create_adapter(cls, task_type: str) -> BaseTaskAdapter:
        """Instantiate and return the registered TaskAdapter for task_type."""
        adapter_cls = TaskRegistry.get_adapter_class(task_type)
        if not adapter_cls:
            raise WorkflowException(
                f"No AI task adapter registered for task type '{task_type}'."
            )
        return adapter_cls()
