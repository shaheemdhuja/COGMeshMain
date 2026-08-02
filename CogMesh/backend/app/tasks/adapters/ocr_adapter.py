"""OCRAdapter executing optical character recognition using TesseractProvider."""

import asyncio
import time
from typing import Any, Dict, List

from app.tasks.base import BaseTaskAdapter
from app.tasks.enums import TaskStatus
from app.tasks.providers.tesseract_provider import TesseractProvider
from app.tasks.result import TaskResult


class OCRAdapter(BaseTaskAdapter):
    """Task adapter executing OCR operations via TesseractProvider."""

    def __init__(self):
        self.provider = TesseractProvider()

    @property
    def adapter_name(self) -> str:
        return "OCRAdapter"

    @property
    def provider_name(self) -> str:
        return "TesseractProvider"

    @property
    def model_name(self) -> str:
        return "tesseract-ocr"

    def supported_capabilities(self) -> List[str]:
        return ["OCR"]

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return isinstance(input_data, dict)

    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        return isinstance(output_data, dict) and ("text" in output_data or "error" in output_data)

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

        ocr_res = await self.provider.extract_text(input_data)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        if "error" in ocr_res and "text" not in ocr_res:
            return TaskResult(
                status=TaskStatus.FAILURE,
                output=ocr_res,
                execution_time_ms=elapsed_ms,
                adapter_name=self.adapter_name,
                provider_name=self.provider_name,
                model_name=self.model_name,
                metadata={"provider_error": True},
            )

        return TaskResult(
            status=TaskStatus.SUCCESS,
            output=ocr_res,
            execution_time_ms=elapsed_ms,
            adapter_name=self.adapter_name,
            provider_name=self.provider_name,
            model_name=self.model_name,
            metadata={"tesseract_execution": True},
        )
