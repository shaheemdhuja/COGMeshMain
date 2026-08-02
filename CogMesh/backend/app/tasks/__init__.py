"""AI Task Adapter Layer package initialization and default adapter registration."""

from app.tasks.enums import TaskStatus
from app.tasks.result import TaskResult
from app.tasks.base import BaseTaskAdapter
from app.tasks.registry import TaskRegistry
from app.tasks.factory import AdapterFactory
from app.tasks.adapters import OCRAdapter, SummaryAdapter, TranslationAdapter, MCQAdapter

# Auto-register standard default adapters into TaskRegistry
TaskRegistry.register("OCR", OCRAdapter)
TaskRegistry.register("SUMMARIZATION", SummaryAdapter)
TaskRegistry.register("TRANSLATION", TranslationAdapter)
TaskRegistry.register("MCQ_GENERATION", MCQAdapter)

__all__ = [
    "TaskStatus",
    "TaskResult",
    "BaseTaskAdapter",
    "TaskRegistry",
    "AdapterFactory",
    "OCRAdapter",
    "SummaryAdapter",
    "TranslationAdapter",
    "MCQAdapter",
]
