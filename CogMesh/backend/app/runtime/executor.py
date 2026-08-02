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

        # Mock results based on task type
        mock_output: Dict[str, Any]
        if assignment.task_type == TaskType.OCR:
            mock_output = {
                "text": "Simulated extracted text from lecture document...",
                "confidence": 0.98,
                "word_count": 142,
            }
        elif assignment.task_type == TaskType.SUMMARIZATION:
            mock_output = {
                "summary": "Simulated summary of lecture text focusing on distributed edge intelligence...",
                "compression_ratio": 0.35,
            }
        elif assignment.task_type == TaskType.TRANSLATION:
            mock_output = {
                "translated_text": "Texto simulado de la conferencia sobre inteligencia distribuida...",
                "target_language": "Spanish",
            }
        elif assignment.task_type == TaskType.MCQ_GENERATION:
            mock_output = {
                "questions": [
                    {
                        "q": "What is CogMesh?",
                        "options": ["Edge AI Runtime", "Database", "Operating System"],
                        "answer": "Edge AI Runtime",
                    }
                ]
            }
        else:
            mock_output = {"output": f"Simulated output for operation {assignment.task_type.value}"}

        result = {
            "node_id": assignment.node_id,
            "device_id": assignment.device_id,
            "task_type": assignment.task_type.value,
            "status": "COMPLETED",
            "output": mock_output,
            "metrics": {
                "execution_time_ms": elapsed_ms,
                "cpu_usage_percent": 35.5,
                "ram_usage_mb": 128.0,
                "energy_cost_joules": 4.2,
            },
        }

        logger.info(
            f"[FakeExecutor] Completed task '{assignment.task_type.value}' ({assignment.node_id}) in {elapsed_ms}ms"
        )
        return result
