"""WorkflowGenerator enforcing capability constraints before producing ExecutionDAGs."""

from typing import List, Set
from loguru import logger

from app.core.exceptions import MissingCapabilityException, WorkflowException
from app.domain.structured_goal import StructuredGoal
from app.models.capability import Capability
from app.workflow.dag import ExecutionDAG
from app.workflow.edge import ExecutionEdge
from app.workflow.enums import TaskType
from app.workflow.node import ExecutionNode


class WorkflowGenerator:
    """Generates capability-constrained ExecutionDAGs from StructuredGoals and active Capability telemetry."""

    @staticmethod
    def generate(goal: StructuredGoal, capabilities: List[Capability]) -> ExecutionDAG:
        """Validate capability constraints and generate a valid ExecutionDAG for the goal."""
        if not goal.operations:
            raise WorkflowException("Cannot generate workflow for goal with empty operations.")

        # 1. Collect all available capabilities across the edge mesh
        available_capabilities: Set[str] = set()
        for cap in capabilities:
            if cap.supported_tasks:
                for task in cap.supported_tasks:
                    available_capabilities.add(task.upper())

        # 2. CAPABILITY CONSTRAINT CHECK (Central CogMesh Contribution)
        # Validate that every required operation is supported by at least one device in the mesh
        for req_op in goal.operations:
            req_op_upper = req_op.upper()
            if req_op_upper not in available_capabilities:
                logger.warning(
                    f"Capability constraint violation: required task '{req_op_upper}' "
                    f"is not supported by any active device in the mesh."
                )
                raise MissingCapabilityException(req_op_upper)

        # 3. Instantiate DAG container
        dag = ExecutionDAG(goal_id=goal.goal_id)
        previous_node: ExecutionNode | None = None

        # 4. Generate sequential task nodes and dependency edges
        for op in goal.operations:
            op_upper = op.upper()
            try:
                task_enum = TaskType(op_upper)
            except ValueError:
                task_enum = TaskType.UNKNOWN

            node = ExecutionNode(
                task_type=task_enum,
                required_capabilities=[op_upper],
                estimated_cost=1.0,
                metadata={"original_operation": op},
            )

            dag.add_node(node)

            if previous_node is not None:
                edge = ExecutionEdge(
                    source=previous_node.node_id,
                    destination=node.node_id,
                )
                dag.add_edge(edge)

            previous_node = node

        # 5. Validate DAG (verifies zero cycles and valid edge references)
        dag.validate()
        logger.info(
            f"Successfully generated ExecutionDAG '{dag.dag_id}' for goal '{goal.goal_id}' "
            f"with {len(dag.nodes)} nodes and {len(dag.edges)} edges."
        )
        return dag
