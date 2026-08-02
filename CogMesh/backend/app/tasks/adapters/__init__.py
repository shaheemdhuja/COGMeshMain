"""AI Task Adapters collection export."""

from app.tasks.adapters.ocr_adapter import OCRAdapter
from app.tasks.adapters.summarization_adapter import SummaryAdapter
from app.tasks.adapters.translation_adapter import TranslationAdapter
from app.tasks.adapters.mcq_adapter import MCQAdapter

__all__ = [
    "OCRAdapter",
    "SummaryAdapter",
    "TranslationAdapter",
    "MCQAdapter",
]
