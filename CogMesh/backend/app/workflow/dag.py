"""ExecutionDAG graph structure maintaining nodes, edges, validation, and topological sorting."""

import uuid
from collections import deque
from typing import Dict, List
from pydantic import BaseModel, Field

from app.core.exceptions import WorkflowException
from app.workflow.edge import ExecutionEdge
from app.workflow.node import ExecutionNode


class ExecutionDAG(BaseModel):
    """Directed Acyclic Graph (DAG) container for workflow task nodes and dependency edges."""

    dag_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the execution DAG.",
    )
    goal_id: str = Field(
        ...,
        description="Goal ID associated with this workflow DAG.",
    )
    nodes: Dict[str, ExecutionNode] = Field(
        default_factory=dict,
        description="Map of node_id to ExecutionNode instances.",
    )
    edges: List[ExecutionEdge] = Field(
        default_factory=list,
        description="List of ExecutionEdge dependency links.",
    )

    def add_node(self, node: ExecutionNode) -> None:
        """Add an execution node to the DAG graph."""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: ExecutionEdge) -> None:
        """Add a directed edge link between source and destination nodes."""
        if edge.source not in self.nodes:
            raise WorkflowException(f"Edge source node '{edge.source}' does not exist in DAG.")
        if edge.destination not in self.nodes:
            raise WorkflowException(f"Edge destination node '{edge.destination}' does not exist in DAG.")

        self.edges.append(edge)
        # Ensure destination node tracks source in its dependencies list
        dest_node = self.nodes[edge.destination]
        if edge.source not in dest_node.dependencies:
            dest_node.dependencies.append(edge.source)

    def validate(self) -> bool:
        """Validate DAG integrity (verifies edge references and checks cycle freedom)."""
        for edge in self.edges:
            if edge.source not in self.nodes:
                raise WorkflowException(f"Invalid edge: source '{edge.source}' not found.")
            if edge.destination not in self.nodes:
                raise WorkflowException(f"Invalid edge: destination '{edge.destination}' not found.")

        # Execute topological sort to ensure zero cycles
        self.topological_sort()
        return True

    def topological_sort(self) -> List[ExecutionNode]:
        """Perform topological sorting using Kahn's Algorithm. Raises WorkflowException if cycle is detected."""
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self.nodes}
        adj_list: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}

        # Build in-degree counts and adjacency graph
        for edge in self.edges:
            adj_list[edge.source].append(edge.destination)
            in_degree[edge.destination] += 1

        # Queue nodes with in-degree == 0
        queue: deque[str] = deque([node_id for node_id, count in in_degree.items() if count == 0])
        sorted_nodes: List[ExecutionNode] = []

        while queue:
            curr_id = queue.popleft()
            sorted_nodes.append(self.nodes[curr_id])

            for neighbor_id in adj_list[curr_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        if len(sorted_nodes) != len(self.nodes):
            raise WorkflowException("Cycle detected in ExecutionDAG graph. Cannot perform topological ordering.")

        return sorted_nodes
