"""Abstract BaseTaskAdapter defining unified contract for all AI task execution adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.tasks.result import TaskResult


class BaseTaskAdapter(ABC):
    """Abstract interface hiding AI model details behind a unified task execution API."""

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Name of the task adapter implementation class."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the underlying AI provider (e.g. MockOCRProvider, TesseractProvider)."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the underlying AI model (e.g. mock-tesseract-v5, gemma-2b)."""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> TaskResult:
        """Execute task using adapter implementation and return TaskResult."""
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input payload parameters before execution."""
        pass

    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output payload structure post-execution."""
        pass

    @abstractmethod
    def supported_capabilities(self) -> List[str]:
        """Return list of supported task capabilities (e.g. ['OCR'])."""
        pass
