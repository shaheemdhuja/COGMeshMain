"""SummaryAdapter providing deterministic mock text summarization."""

import asyncio
import time
from typing import Any, Dict, List

from app.tasks.base import BaseTaskAdapter
from app.tasks.enums import TaskStatus
from app.tasks.result import TaskResult


class SummaryAdapter(BaseTaskAdapter):
    """Task adapter executing text summarization via mock LLM provider."""

    @property
    def adapter_name(self) -> str:
        return "SummaryAdapter"

    @property
    def provider_name(self) -> str:
        return "MockGemmaProvider"

    @property
    def model_name(self) -> str:
        return "mock-gemma-2b"

    def supported_capabilities(self) -> List[str]:
        return ["SUMMARIZATION"]

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return isinstance(input_data, dict)

    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        return isinstance(output_data, dict) and "summary" in output_data

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
            "summary": "Summary: CogMesh coordinates edge nodes into a capability-constrained collaborative AI runtime.",
            "key_points": [
                "Distributed task scheduling across edge nodes",
                "Capability constraint enforcement prior to execution",
                "Transport-independent mesh communication layer",
            ],
            "compression_ratio": 0.40,
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
