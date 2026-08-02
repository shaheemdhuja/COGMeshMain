"""AdaptiveScheduler executing optimal device selection and ExecutionPlan creation."""

from typing import Dict, List, Tuple
from loguru import logger

from app.core.exceptions import NoEligibleDeviceException
from app.models.capability import Capability
from app.models.device import Device
from app.scheduler.assignment import TaskAssignment
from app.scheduler.planner import ExecutionPlan
from app.scheduler.scoring import SchedulingScore
from app.workflow.dag import ExecutionDAG


class AdaptiveScheduler:
    """Adaptive task scheduler assigning DAG nodes to optimal edge devices using weighted scoring."""

    @staticmethod
    def schedule_dag(
        dag: ExecutionDAG,
        devices: List[Device],
        capabilities: List[Capability],
    ) -> ExecutionPlan:
        """Map each ExecutionNode in topological order to an optimal edge device and generate an ExecutionPlan."""
        # 1. Map capability snapshots by device_id
        cap_map: Dict[str, Capability] = {c.device_id: c for c in capabilities}

        # 2. Extract topological node execution sequence
        sorted_nodes = dag.topological_sort()

        assignments: List[TaskAssignment] = []

        # 3. Schedule each node sequentially
        for node in sorted_nodes:
            candidates: List[Tuple[float, Device, Capability, str]] = []

            for dev in devices:
                cap = cap_map.get(dev.id)
                score, reason = SchedulingScore.calculate_score(
                    device=dev,
                    capability=cap,
                    required_capabilities=node.required_capabilities,
                )
                if score > 0.0 and cap is not None:
                    candidates.append((score, dev, cap, reason))

            # If no eligible device found -> fail scheduling with HTTP 409
            if not candidates:
                logger.warning(
                    f"Scheduling failed: no online/capable device available for task '{node.task_type}' "
                    f"requiring capabilities {node.required_capabilities}"
                )
                raise NoEligibleDeviceException(str(node.task_type.value))

            # Sort candidates by:
            # 1. Highest total score
            # 2. Highest battery level
            # 3. Highest RAM
            candidates.sort(
                key=lambda item: (item[0], item[2].battery_level, item[2].ram_gb),
                reverse=True,
            )

            best_score, best_dev, best_cap, best_reason = candidates[0]

            assignment = TaskAssignment(
                node_id=node.node_id,
                device_id=best_dev.id,
                task_type=node.task_type,
                priority=1,
                reason=f"Assigned to {best_dev.device_name} ({best_dev.id}) - {best_reason}",
                estimated_duration=round(node.estimated_cost * 2.0, 2),
            )
            assignments.append(assignment)

            logger.info(
                f"Scheduler assigned task '{node.task_type}' ({node.node_id}) -> "
                f"Device '{best_dev.device_name}' ({best_dev.id}) with score {best_score:.3f}"
            )

        # 4. Construct ExecutionPlan
        execution_plan = ExecutionPlan(
            goal_id=dag.goal_id,
            workflow_id=dag.dag_id,
            assignments=assignments,
        )
        return execution_plan
