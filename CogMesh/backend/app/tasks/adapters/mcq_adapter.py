"""MCQAdapter providing deterministic mock multiple choice question generation."""

import asyncio
import time
from typing import Any, Dict, List

from app.tasks.base import BaseTaskAdapter
from app.tasks.enums import TaskStatus
from app.tasks.result import TaskResult


class MCQAdapter(BaseTaskAdapter):
    """Task adapter executing MCQ question generation via mock LLM provider."""

    @property
    def adapter_name(self) -> str:
        return "MCQAdapter"

    @property
    def provider_name(self) -> str:
        return "MockLlamaProvider"

    @property
    def model_name(self) -> str:
        return "mock-llama-3b"

    def supported_capabilities(self) -> List[str]:
        return ["MCQ_GENERATION"]

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return isinstance(input_data, dict)

    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        return isinstance(output_data, dict) and "questions" in output_data

    async def execute(self, input_data: Dict[str, Any]) -> TaskResult:
        start = time.perf_counter()
        if not self.validate_input(input_data):
            return TaskResult(
                status=TaskStatus.INVALID_INPUT,
                adapter_name=self.adapter_name,
                provider_name=self.provider_name,
                model_name=self.model_name,
                output={"error": "Invalid input format"},
            )

        await asyncio.sleep(0.02)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        output = {
            "questions": [
                {
                    "id": 1,
                    "question": "What is the primary role of the CogMesh Runtime?",
                    "options": [
                        "Collaborative multi-device edge AI runtime",
                        "Relational database engine",
                        "Single-threaded browser extension",
                        "Web server framework",
                    ],
                    "correct_answer": "Collaborative multi-device edge AI runtime",
                },
                {
                    "id": 2,
                    "question": "How are task capability constraints enforced in CogMesh?",
                    "options": [
                        "Prior to execution in Workflow Generator and Scheduler",
                        "During post-execution logging",
                        "By random node selection",
                        "They are not enforced",
                    ],
                    "correct_answer": "Prior to execution in Workflow Generator and Scheduler",
                },
            ]
        }

        return TaskResult(
            status=TaskStatus.SUCCESS,
            output=output,
            execution_time_ms=elapsed_ms,
            adapter_name=self.adapter_name,
            provider_name=self.provider_name,
            model_name=self.model_name,
            metadata={"simulated": True},
        )
