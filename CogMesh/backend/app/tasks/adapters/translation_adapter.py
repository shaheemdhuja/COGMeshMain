"""TranslationAdapter providing deterministic mock text translation."""

import asyncio
import time
from typing import Any, Dict, List

from app.tasks.base import BaseTaskAdapter
from app.tasks.enums import TaskStatus
from app.tasks.result import TaskResult


class TranslationAdapter(BaseTaskAdapter):
    """Task adapter executing neural translation via mock provider."""

    @property
    def adapter_name(self) -> str:
        return "TranslationAdapter"

    @property
    def provider_name(self) -> str:
        return "MockNllbProvider"

    @property
    def model_name(self) -> str:
        return "mock-nllb-200"

    def supported_capabilities(self) -> List[str]:
        return ["TRANSLATION"]

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return isinstance(input_data, dict)

    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        return isinstance(output_data, dict) and "translated_text" in output_data

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
            "translated_text": "Resumen: La arquitectura CogMesh permite la inteligencia colaborativa en el borde.",
            "source_language": input_data.get("source_lang", "English"),
            "target_language": input_data.get("target_lang", "Spanish"),
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
