"""WorkflowOptimizer optimizing DAG structures (duplicate node removal, edge compaction)."""

from typing import List, Dict
from loguru import logger

from app.workflow.dag import ExecutionDAG
from app.workflow.edge import ExecutionEdge
from app.workflow.node import ExecutionNode


class WorkflowOptimizer:
    """Optimizes generated ExecutionDAG graphs without modifying scheduling or device assignments."""

    @staticmethod
    def optimize(dag: ExecutionDAG) -> ExecutionDAG:
        """Optimize execution graph by eliminating consecutive duplicate operations and compacting edges."""
        if not dag.nodes:
            return dag

        sorted_nodes = dag.topological_sort()
        if len(sorted_nodes) <= 1:
            return dag

        optimized_dag = ExecutionDAG(goal_id=dag.goal_id, dag_id=dag.dag_id)
        filtered_nodes: List[ExecutionNode] = []
        replaced_nodes_map: Dict[str, str] = {}  # duplicate_node_id -> kept_node_id

        for node in sorted_nodes:
            if not filtered_nodes:
                filtered_nodes.append(node)
                continue

            last_kept_node = filtered_nodes[-1]
            # Check if current node is a duplicate of the immediately preceding node
            if node.task_type == last_kept_node.task_type and node.required_capabilities == last_kept_node.required_capabilities:
                logger.info(
                    f"WorkflowOptimizer: Merging duplicate consecutive task node '{node.task_type}' ({node.node_id}) "
                    f"into existing node ({last_kept_node.node_id})"
                )
                replaced_nodes_map[node.node_id] = last_kept_node.node_id
            else:
                filtered_nodes.append(node)

        # Add kept nodes to optimized DAG
        for node in filtered_nodes:
            # Clear old dependencies to re-link
            node.dependencies = []
            optimized_dag.add_node(node)

        # Re-link edges using replaced nodes mapping
        for edge in dag.edges:
            src = replaced_nodes_map.get(edge.source, edge.source)
            dest = replaced_nodes_map.get(edge.destination, edge.destination)

            # Skip self-loop edges created by merging duplicate adjacent nodes
            if src != dest and src in optimized_dag.nodes and dest in optimized_dag.nodes:
                # Avoid duplicate edge creation
                edge_exists = any(
                    e.source == src and e.destination == dest for e in optimized_dag.edges
                )
                if not edge_exists:
                    new_edge = ExecutionEdge(source=src, destination=dest)
                    optimized_dag.add_edge(new_edge)

        # Re-validate optimized graph
        optimized_dag.validate()
        return optimized_dag
