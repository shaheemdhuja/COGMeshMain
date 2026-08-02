"""Scheduler Service orchestrating execution planning, candidate evaluation, and Task persistence."""

from typing import List
from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, GoalNotFoundException
from app.database.repository.capability_repository import CapabilityRepository
from app.database.repository.device_repository import DeviceRepository
from app.database.repository.goal_repository import GoalRepository
from app.database.repository.task_repository import TaskRepository
from app.models.task import Task
from app.scheduler.assignment import TaskAssignment
from app.scheduler.planner import ExecutionPlan
from app.scheduler.scheduler import AdaptiveScheduler
from app.services.workflow_service import WorkflowService
from app.workflow.enums import TaskType


class SchedulerService:
    """Service layer managing adaptive task scheduling and execution plan persistence."""

    @staticmethod
    async def create_execution_plan(db: AsyncSession, goal_id: str) -> ExecutionPlan:
        """Evaluate edge devices, score candidates, generate ExecutionPlan, and persist tasks in SQLite."""
        # 1. Validate Goal exists
        goal_repo = GoalRepository(db)
        goal_entity = await goal_repo.get_by_id(goal_id)
        if not goal_entity:
            raise GoalNotFoundException(goal_id)

        # 2. Retrieve generated ExecutionDAG workflow
        dag = await WorkflowService.get_workflow(db, goal_id)

        # 3. Retrieve active devices and capability snapshots
        dev_repo = DeviceRepository(db)
        devices = await dev_repo.get_all()

        cap_repo = CapabilityRepository(db)
        capabilities = await cap_repo.get_all()

        # 4. Execute Adaptive Scheduling engine
        execution_plan = AdaptiveScheduler.schedule_dag(dag, devices, capabilities)

        # 5. Persist scheduled task assignments in SQLite database
        task_repo = TaskRepository(db)

        # Clear previous scheduled tasks for this workflow if re-scheduling
        await db.execute(delete(Task).where(Task.workflow_id == dag.dag_id))

        for assignment in execution_plan.assignments:
            task_entity = Task(
                id=assignment.node_id,
                workflow_id=dag.dag_id,
                task_type=str(assignment.task_type.value),
                payload={
                    "plan_id": execution_plan.plan_id,
                    "reason": assignment.reason,
                    "estimated_duration": assignment.estimated_duration,
                    "priority": assignment.priority,
                },
                status="SCHEDULED",
                assigned_device_id=assignment.device_id,
            )
            await task_repo.create(task_entity)

        logger.info(
            f"Successfully generated and stored ExecutionPlan '{execution_plan.plan_id}' "
            f"for goal '{goal_id}' with {len(execution_plan.assignments)} task assignments."
        )
        return execution_plan

    @staticmethod
    async def get_execution_plan(db: AsyncSession, goal_id: str) -> ExecutionPlan:
        """Retrieve the latest ExecutionPlan for a goal from database persistence."""
        goal_repo = GoalRepository(db)
        goal_entity = await goal_repo.get_by_id(goal_id)
        if not goal_entity:
            raise GoalNotFoundException(goal_id)

        dag = await WorkflowService.get_workflow(db, goal_id)

        task_repo = TaskRepository(db)
        tasks = await task_repo.get_by_workflow_id(dag.dag_id)

        if not tasks:
            raise EntityNotFoundException("ExecutionPlan", goal_id)

        assignments: List[TaskAssignment] = []
        stored_plan_id: Optional[str] = None

        for t in tasks:
            payload = t.payload or {}
            if not stored_plan_id and "plan_id" in payload:
                stored_plan_id = payload["plan_id"]

            try:
                task_enum = TaskType(t.task_type)
            except ValueError:
                task_enum = TaskType.UNKNOWN

            assignment = TaskAssignment(
                node_id=t.id,
                device_id=t.assigned_device_id or "",
                task_type=task_enum,
                priority=payload.get("priority", 1),
                reason=payload.get("reason", "Loaded from persistent database"),
                estimated_duration=payload.get("estimated_duration", 1.0),
            )
            assignments.append(assignment)

        plan_kwargs = {
            "goal_id": goal_id,
            "workflow_id": dag.dag_id,
            "assignments": assignments,
        }
        if stored_plan_id:
            plan_kwargs["plan_id"] = stored_plan_id

        return ExecutionPlan(**plan_kwargs)

