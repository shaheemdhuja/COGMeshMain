"""Goal Service parsing natural language requests into deterministic StructuredGoal objects."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import GoalNotFoundException, GoalParsingException
from app.database.repository.goal_repository import GoalRepository
from app.domain.structured_goal import StructuredGoal
from app.models.goal import Goal


class GoalService:
    """Service layer converting natural language user goals into StructuredGoal domain objects."""

    @staticmethod
    def parse_natural_language(natural_language_goal: str, file_path: Optional[str] = None) -> StructuredGoal:
        """Deterministic rule-based parser mapping natural language input to a StructuredGoal."""
        if not natural_language_goal or not natural_language_goal.strip():
            logger.warning("Rejecting empty or whitespace goal parsing request")
            raise GoalParsingException("Natural language goal input cannot be empty.")

        text = natural_language_goal.strip()
        lower_text = text.lower()

        # 1. Determine goal_type
        if any(k in lower_text for k in ["lecture", "class", "course", "slide"]):
            goal_type = "lecture_processing"
        elif any(k in lower_text for k in ["ocr", "scan", "document", "pdf"]):
            goal_type = "document_pipeline"
        else:
            goal_type = "general_pipeline"

        # 2. Determine input_type
        if file_path:
            input_type = "pdf" if file_path.lower().endswith(".pdf") else "image"
        elif "pdf" in lower_text:
            input_type = "pdf"
        elif any(k in lower_text for k in ["image", "png", "jpg", "photo", "scan"]):
            input_type = "image"
        elif any(k in lower_text for k in ["text", "txt", "string", "doc"]):
            input_type = "text"
        else:
            input_type = "pdf" if goal_type == "lecture_processing" else "unknown"

        # 3. Detect atomic operations (Ordered sequence based on workflow dependencies)
        operations: List[str] = []

        # OCR operation
        if file_path or any(k in lower_text for k in ["ocr", "scan", "extract text", "pdf", "lecture"]):
            operations.append("OCR")

        # Summarization operation
        if any(k in lower_text for k in ["summarize", "summary", "abstract", "overview", "shorten"]):
            operations.append("SUMMARIZATION")

        # Translation operation
        if any(k in lower_text for k in ["translate", "translation", "spanish", "french", "german", "hindi"]):
            operations.append("TRANSLATION")

        # MCQ Generation operation
        if any(k in lower_text for k in ["mcq", "quiz", "question", "test", "multiple choice"]):
            operations.append("MCQ_GENERATION")

        # Reject if no recognized operations
        if not operations:
            logger.warning(f"Unable to parse operations from input: '{text}'")
            raise GoalParsingException(
                "Unable to identify any supported AI operations from input.",
                details={"input": text},
            )

        # 4. Determine priority
        priority = 2 if any(k in lower_text for k in ["urgent", "high priority", "critical", "fast"]) else 1

        # 5. Extract constraints (e.g. target language if translation requested)
        constraints: Dict[str, Any] = {}
        import re
        match = re.search(r"translate\s+(?:the\s+text\s+|the\s+document\s+|this\s+)?to\s+([a-zA-Z]+)", lower_text)
        if match:
            constraints["target_language"] = match.group(1).capitalize()
        else:
            languages = [
                "malayalam", "tamil", "telugu", "bengali", "kannada", "marathi", "gujarati", "punjabi", "urdu",
                "spanish", "french", "german", "hindi", "japanese", "chinese", "arabic", "italian", "russian",
                "korean", "portuguese", "dutch", "turkish", "greek", "vietnamese", "thai", "indonesian"
            ]
            for lang in languages:
                if lang in lower_text:
                    constraints["target_language"] = lang.capitalize()
                    break

        metadata: Dict[str, Any] = {
            "parsed_at": datetime.now(timezone.utc).isoformat(),
            "parser_strategy": "deterministic_rule_based",
        }
        if file_path:
            metadata["file_path"] = file_path

        # Construct StructuredGoal
        structured_goal = StructuredGoal(
            natural_language_input=text,
            goal_type=goal_type,
            input_type=input_type,
            operations=operations,
            priority=priority,
            constraints=constraints,
            metadata=metadata,
        )

        logger.info(
            f"Successfully parsed goal '{structured_goal.goal_id}' with operations: {structured_goal.operations}"
        )
        return structured_goal

    @classmethod
    async def parse_and_store_goal(
        cls, db: AsyncSession, natural_language_goal: str, file_path: Optional[str] = None
    ) -> StructuredGoal:
        """Parse natural language into StructuredGoal and persist Goal entity in SQLite."""
        structured_goal = cls.parse_natural_language(natural_language_goal, file_path=file_path)


        # Persist to database
        goal_repo = GoalRepository(db)
        goal_entity = Goal(
            id=structured_goal.goal_id,
            natural_language_input=structured_goal.natural_language_input,
            structured_goal=structured_goal.model_dump(),
            status="PARSED",
        )
        await goal_repo.create(goal_entity)
        return structured_goal

    @staticmethod
    async def get_goal_by_id(db: AsyncSession, goal_id: str) -> Goal:
        """Retrieve a stored Goal record from the database."""
        goal_repo = GoalRepository(db)
        goal = await goal_repo.get_by_id(goal_id)
        if not goal:
            raise GoalNotFoundException(goal_id)
        return goal
