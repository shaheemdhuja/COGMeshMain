"""TranslationAdapter executing neural text translation via TranslationProvider."""

import asyncio
import time
from typing import Any, Dict, List

from app.tasks.base import BaseTaskAdapter
from app.tasks.enums import TaskStatus
from app.tasks.providers.translation_provider import TranslationProvider
from app.tasks.result import TaskResult


class TranslationAdapter(BaseTaskAdapter):
    """Task adapter executing neural machine translation via TranslationProvider."""

    def __init__(self):
        self.provider = TranslationProvider()

    @property
    def adapter_name(self) -> str:
        return "TranslationAdapter"

    @property
    def provider_name(self) -> str:
        return "TranslationProvider"

    @property
    def model_name(self) -> str:
        return "nllb-200"

    def supported_capabilities(self) -> List[str]:
        return ["TRANSLATION"]

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return isinstance(input_data, dict)

    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        return isinstance(output_data, dict) and ("translated_text" in output_data or "error" in output_data)

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

        text_content = input_data.get("text")
        if not text_content and "user_prompt" in input_data:
            prompt_str = input_data["user_prompt"]
            import re
            match = re.search(r'["\']([^"\']+)["\']', prompt_str)
            if match:
                text_content = match.group(1)
            else:
                match_phrase = re.search(r"translate\s+(?:the\s+text\s+|the\s+document\s+|this\s+)?(.+?)\s+to\s+[a-zA-Z]+", prompt_str, re.IGNORECASE)
                if match_phrase:
                    text_content = match_phrase.group(1).strip()

        if not text_content:
            text_content = "CogMesh architecture enables collaborative multi-device edge intelligence."

        source_lang = input_data.get("source_lang", "English")
        target_lang = input_data.get("target_lang", "Spanish")


        trans_res = await self.provider.translate(
            text=text_content,
            source_lang=source_lang,
            target_lang=target_lang,
        )
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return TaskResult(
            status=TaskStatus.SUCCESS,
            output=trans_res,
            execution_time_ms=elapsed_ms,
            adapter_name=self.adapter_name,
            provider_name=self.provider_name,
            model_name=self.model_name,
            metadata={"translation_execution": True},
        )
