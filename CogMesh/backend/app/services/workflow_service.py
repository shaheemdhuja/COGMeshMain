"""Workflow Service orchestrating DAG generation, capability validation, optimization, and DB persistence."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, GoalNotFoundException
from app.database.repository.capability_repository import CapabilityRepository
from app.database.repository.goal_repository import GoalRepository
from app.database.repository.workflow_repository import WorkflowRepository
from app.domain.structured_goal import StructuredGoal
from app.models.workflow import Workflow
from app.workflow.dag import ExecutionDAG
from app.workflow.enums import WorkflowStatus
from app.workflow.generator import WorkflowGenerator
from app.workflow.optimizer import WorkflowOptimizer


class WorkflowService:
    """Service layer managing workflow generation, optimization, and retrieval."""

    @staticmethod
    async def generate_workflow(db: AsyncSession, goal_id: str) -> ExecutionDAG:
        """Generate and optimize a capability-constrained ExecutionDAG for a specific goal."""
        # 1. Fetch Goal
        goal_repo = GoalRepository(db)
        goal_entity = await goal_repo.get_by_id(goal_id)
        if not goal_entity:
            raise GoalNotFoundException(goal_id)

        # Reconstruct StructuredGoal
        structured_goal = StructuredGoal.model_validate(goal_entity.structured_goal)

        # 2. Fetch Active Capability Snapshots
        cap_repo = CapabilityRepository(db)
        capabilities = await cap_repo.get_all()

        # 3. Generate Capability-Constrained DAG
        raw_dag = WorkflowGenerator.generate(structured_goal, capabilities)

        # 4. Optimize DAG (remove duplicate operations, compact edges)
        optimized_dag = WorkflowOptimizer.optimize(raw_dag)

        # 5. Persist Workflow definition in database
        wf_repo = WorkflowRepository(db)
        existing_wf = await wf_repo.get_by_goal_id(goal_id)

        if existing_wf:
            existing_wf.dag_structure = optimized_dag.model_dump()
            existing_wf.status = WorkflowStatus.OPTIMIZED.value
            await wf_repo.update(existing_wf)
        else:
            new_wf = Workflow(
                id=optimized_dag.dag_id,
                goal_id=goal_id,
                dag_structure=optimized_dag.model_dump(),
                status=WorkflowStatus.OPTIMIZED.value,
            )
            await wf_repo.create(new_wf)

        logger.info(f"Successfully generated and stored Workflow DAG for goal '{goal_id}'")
        return optimized_dag

    @staticmethod
    async def get_workflow(db: AsyncSession, goal_id: str) -> ExecutionDAG:
        """Retrieve the generated ExecutionDAG for a specific goal."""
        goal_repo = GoalRepository(db)
        goal_entity = await goal_repo.get_by_id(goal_id)
        if not goal_entity:
            raise GoalNotFoundException(goal_id)

        wf_repo = WorkflowRepository(db)
        wf_entity = await wf_repo.get_by_goal_id(goal_id)
        if not wf_entity:
            raise EntityNotFoundException("Workflow", goal_id)

        return ExecutionDAG.model_validate(wf_entity.dag_structure)
