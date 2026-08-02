"""Task Service managing adapter execution and database persistence for AI task audits."""

from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository.base import BaseRepository
from app.models.task_execution_audit import TaskExecutionAudit
from app.tasks.factory import AdapterFactory
from app.tasks.registry import TaskRegistry
from app.tasks.result import TaskResult


class TaskService:
    """Service layer providing available adapter listings, task execution dispatch, and SQLite persistence."""

    @classmethod
    def list_adapters(cls) -> List[Dict[str, Any]]:
        """Retrieve list of registered task adapters and supported capabilities."""
        return TaskRegistry.list_adapters()

    @classmethod
    async def execute_task(
        cls,
        db: AsyncSession,
        task_type: str,
        input_data: Dict[str, Any],
    ) -> TaskResult:
        """Instantiate task adapter via AdapterFactory, execute input payload, and record SQLite audit entry."""
        adapter = AdapterFactory.create_adapter(task_type)
        result = await adapter.execute(input_data)

        # Persist audit record in SQLite
        audit_entry = TaskExecutionAudit(
            task_id=result.task_id,
            task_type=task_type.upper(),
            status=result.status.value,
            adapter_name=result.adapter_name,
            provider_name=result.provider_name,
            model_name=result.model_name,
            execution_time_ms=result.execution_time_ms,
            output_metadata=result.output,
        )
        repo = BaseRepository[TaskExecutionAudit](TaskExecutionAudit, db)
        await repo.create(audit_entry)

        return result
