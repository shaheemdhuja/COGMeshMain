import asyncio
import time
from typing import TYPE_CHECKING, Any, Dict, Optional
from loguru import logger

from app.scheduler.assignment import TaskAssignment
from app.workflow.enums import TaskType

if TYPE_CHECKING:
    from app.domain.execution_context import ExecutionContext



class FakeExecutor:
    """Simulated task executor for testing orchestration workflows without real AI runtime hardware."""

    @classmethod
    async def execute_task(
        cls,
        assignment: TaskAssignment,
        context: Optional[Any] = None,
        simulated_delay: float = 0.05,
    ) -> Dict[str, Any]:

        """Simulate task execution via async sleep and return mock inference results and performance metrics."""
        start_time = time.perf_counter()

        logger.info(
            f"[FakeExecutor] Starting simulated task '{assignment.task_type.value}' ({assignment.node_id}) "
            f"on device '{assignment.device_id}'"
        )

        # Simulate work using non-blocking async sleep
        await asyncio.sleep(simulated_delay)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Execute task through AI Task Adapter Layer (AdapterFactory -> TaskAdapter)
        from app.tasks.factory import AdapterFactory

        task_type_str = str(assignment.task_type.value)
        try:
            adapter = AdapterFactory.create_adapter(task_type_str)
            task_result = await adapter.execute({"node_id": assignment.node_id})
            mock_output = task_result.output
            adapter_name = task_result.adapter_name
            provider_name = task_result.provider_name
            model_name = task_result.model_name
        except Exception:
            mock_output = {"output": f"Simulated output for operation {task_type_str}"}
            adapter_name = "DefaultAdapter"
            provider_name = "DefaultProvider"
            model_name = "default-model"

        result = {
            "node_id": assignment.node_id,
            "device_id": assignment.device_id,
            "task_type": task_type_str,
            "status": "COMPLETED",
            "adapter_name": adapter_name,
            "provider_name": provider_name,
            "model_name": model_name,
            "output": mock_output,
            "metrics": {
                "execution_time_ms": elapsed_ms,
                "cpu_usage_percent": 35.5,
                "ram_usage_mb": 128.0,
                "energy_cost_joules": 4.2,
            },
        }

        logger.info(
            f"[FakeExecutor] Completed task '{task_type_str}' ({assignment.node_id}) "
            f"via adapter '{adapter_name}' in {elapsed_ms}ms"
        )
        return result

