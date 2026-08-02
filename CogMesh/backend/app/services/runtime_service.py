"""Runtime Service orchestrating execution plan dispatch, database log persistence, and status tracking."""

from typing import Dict, Any
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, GoalNotFoundException
from app.database.repository.base import BaseRepository
from app.database.repository.goal_repository import GoalRepository
from app.domain.structured_goal import StructuredGoal
from app.models.metric import ExecutionMetric
from app.models.task_log import TaskLog
from app.domain.execution_context import ExecutionContext
from app.runtime.orchestrator import RuntimeOrchestrator
from app.services.scheduler_service import SchedulerService
from app.services.workflow_service import WorkflowService


class RuntimeService:
    """Service layer managing RuntimeOrchestrator interactions and database audit persistence."""

    @staticmethod
    async def start_execution(db: AsyncSession, goal_id: str) -> ExecutionContext:
        """Fetch Goal, Workflow, ExecutionPlan, execute plan via RuntimeOrchestrator, and persist logs/metrics."""
        # 1. Validate Goal
        goal_repo = GoalRepository(db)
        goal_entity = await goal_repo.get_by_id(goal_id)
        if not goal_entity:
            raise GoalNotFoundException(goal_id)

        structured_goal_data: Dict[str, Any] = goal_entity.structured_goal or {}
        goal = StructuredGoal(**structured_goal_data)

        # 2. Retrieve ExecutionDAG workflow
        dag = await WorkflowService.get_workflow(db, goal_id)

        # 3. Retrieve ExecutionPlan
        plan = await SchedulerService.get_execution_plan(db, goal_id)

        # 4. Dispatch ExecutionPlan to RuntimeOrchestrator
        context = await RuntimeOrchestrator.execute_plan(
            plan=plan,
            goal=goal,
            dag=dag,
            simulated_delay=0.05,
        )

        # 5. Persist RuntimeEvents as TaskLog records in SQLite
        log_repo = BaseRepository[TaskLog](TaskLog, db)
        for event in context.events:
            if event.node_id:
                log_entry = TaskLog(
                    task_id=event.node_id,
                    device_id=event.device_id,
                    log_level="INFO",
                    message=f"[{event.event_type.value}] {event.message}",
                )
                await log_repo.create(log_entry)

        # 6. Persist performance metrics as ExecutionMetric records in SQLite
        metric_repo = BaseRepository[ExecutionMetric](ExecutionMetric, db)
        for node_id, metric_data in context.metrics.items():
            metric_entry = ExecutionMetric(
                goal_id=goal_id,
                task_id=node_id,
                execution_time_ms=metric_data.get("execution_time_ms", 0.0),
                cpu_usage=metric_data.get("cpu_usage_percent", 0.0),
                ram_usage=metric_data.get("ram_usage_mb", 0.0),
                power_consumed=metric_data.get("energy_cost_joules", 0.0),
            )
            await metric_repo.create(metric_entry)

        logger.info(
            f"Execution plan completed for goal '{goal_id}' with status '{context.status.value}'. "
            f"Persisted {len(context.events)} task logs and {len(context.metrics)} metric entries."
        )

        return context

    @staticmethod
    def get_runtime_status(context_id: str) -> ExecutionContext:
        """Retrieve current in-memory status of an active or completed ExecutionContext."""
        context = RuntimeOrchestrator.active_contexts.get(context_id)
        if not context:
            raise EntityNotFoundException("ExecutionContext", context_id)
        return context

    @staticmethod
    def cancel_execution(context_id: str) -> ExecutionContext:
        """Abort execution of an active ExecutionContext."""
        return RuntimeOrchestrator.cancel_execution(context_id)
