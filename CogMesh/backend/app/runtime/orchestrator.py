"""RuntimeOrchestrator managing ExecutionPlan execution, TaskStateMachine, event emissions, and metrics collection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional
from loguru import logger


from app.domain.structured_goal import StructuredGoal
from app.runtime.enums import RuntimeEventType, RuntimeStatus, TaskState
from app.runtime.events import RuntimeEvent
from app.runtime.executor import FakeExecutor
from app.runtime.queue import ExecutionQueue
from app.runtime.state_machine import TaskStateMachine
from app.scheduler.planner import ExecutionPlan
from app.workflow.dag import ExecutionDAG

if TYPE_CHECKING:
    from app.domain.execution_context import ExecutionContext



class RuntimeOrchestrator:
    """Central orchestrator driving task execution queues, state machines, and runtime event streams."""

    # In-memory registry of active and completed execution contexts
    active_contexts: Dict[str, ExecutionContext] = {}

    @classmethod
    def emit_event(
        cls,
        context: ExecutionContext,
        event_type: RuntimeEventType,
        message: str,
        node_id: Optional[str] = None,
        device_id: Optional[str] = None,
        payload: Optional[Dict] = None,
    ) -> RuntimeEvent:
        """Construct, log, and append a RuntimeEvent to the ExecutionContext."""
        event = RuntimeEvent(
            event_type=event_type,
            context_id=context.context_id,
            goal_id=context.goal_id,
            node_id=node_id,
            device_id=device_id,
            message=message,
            payload=payload or {},
        )
        context.events.append(event)
        logger.info(f"[RuntimeEvent] [{event_type.value}] Context {context.context_id}: {message}")
        return event

    @classmethod
    async def execute_plan(
        cls,
        plan: ExecutionPlan,
        goal: StructuredGoal,
        dag: ExecutionDAG,
        simulated_delay: float = 0.05,
    ) -> "ExecutionContext":
        """Execute an ExecutionPlan using FIFO ExecutionQueue and FakeExecutor simulation."""
        from app.domain.execution_context import ExecutionContext

        context = ExecutionContext(
            goal_id=plan.goal_id,
            goal=goal,
            workflow=dag.model_dump() if hasattr(dag, "model_dump") else {},
            status=RuntimeStatus.RUNNING,
        )

        cls.active_contexts[context.context_id] = context

        # 1. Emit PLAN_STARTED event
        cls.emit_event(
            context,
            RuntimeEventType.PLAN_STARTED,
            f"Execution plan '{plan.plan_id}' started with {len(plan.assignments)} task assignments.",
        )

        # 2. Initialize task states to PENDING
        for assignment in plan.assignments:
            context.task_states[assignment.node_id] = TaskState.PENDING.value

        # 3. Populate FIFO queue
        queue = ExecutionQueue()
        for assignment in plan.assignments:
            queue.enqueue(assignment)

        # 4. Sequential execution loop
        while not queue.is_empty():
            # Check for early cancellation
            if context.status == RuntimeStatus.CANCELLED:
                logger.warning(f"Execution context '{context.context_id}' was cancelled. Aborting queue.")
                while not queue.is_empty():
                    cancelled_task = queue.dequeue()
                    if cancelled_task:
                        context.task_states[cancelled_task.node_id] = TaskState.CANCELLED.value
                        cls.emit_event(
                            context,
                            RuntimeEventType.TASK_CANCELLED,
                            f"Task '{cancelled_task.node_id}' cancelled due to execution abort.",
                            node_id=cancelled_task.node_id,
                            device_id=cancelled_task.device_id,
                        )
                break

            assignment = queue.dequeue()
            if not assignment:
                break

            node_id = assignment.node_id
            dev_id = assignment.device_id

            try:
                # Transition PENDING -> READY
                current_st = TaskState(context.task_states[node_id])
                ready_st = TaskStateMachine.transition(current_st, TaskState.READY)
                context.task_states[node_id] = ready_st.value
                cls.emit_event(
                    context,
                    RuntimeEventType.TASK_READY,
                    f"Task '{assignment.task_type.value}' ({node_id}) is READY for device '{dev_id}'.",
                    node_id=node_id,
                    device_id=dev_id,
                )

                # Transition READY -> RUNNING
                running_st = TaskStateMachine.transition(ready_st, TaskState.RUNNING)
                context.task_states[node_id] = running_st.value
                cls.emit_event(
                    context,
                    RuntimeEventType.TASK_STARTED,
                    f"Task '{assignment.task_type.value}' ({node_id}) started on device '{dev_id}'.",
                    node_id=node_id,
                    device_id=dev_id,
                )

                # Simulate AI task execution via FakeExecutor
                task_result = await FakeExecutor.execute_task(
                    assignment=assignment,
                    context=context,
                    simulated_delay=simulated_delay,
                )

                # Transition RUNNING -> COMPLETED
                completed_st = TaskStateMachine.transition(running_st, TaskState.COMPLETED)
                context.task_states[node_id] = completed_st.value

                context.results[node_id] = task_result.get("output", {})
                context.metrics[node_id] = task_result.get("metrics", {})

                cls.emit_event(
                    context,
                    RuntimeEventType.TASK_COMPLETED,
                    f"Task '{assignment.task_type.value}' ({node_id}) COMPLETED successfully.",
                    node_id=node_id,
                    device_id=dev_id,
                    payload=task_result.get("metrics", {}),
                )

            except Exception as e:
                logger.error(f"Error executing task node '{node_id}': {str(e)}")
                context.task_states[node_id] = TaskState.FAILED.value
                context.status = RuntimeStatus.FAILED
                cls.emit_event(
                    context,
                    RuntimeEventType.TASK_FAILED,
                    f"Task '{node_id}' failed: {str(e)}",
                    node_id=node_id,
                    device_id=dev_id,
                )
                break

        # 5. Finalize context status
        if context.status == RuntimeStatus.RUNNING:
            context.status = RuntimeStatus.COMPLETED
            cls.emit_event(
                context,
                RuntimeEventType.PLAN_COMPLETED,
                f"Execution plan '{plan.plan_id}' completed successfully.",
            )

        return context

    @classmethod
    def cancel_execution(cls, context_id: str) -> ExecutionContext:
        """Cancel an active execution context."""
        context = cls.active_contexts.get(context_id)
        if not context:
            from app.core.exceptions import EntityNotFoundException
            raise EntityNotFoundException("ExecutionContext", context_id)

        context.status = RuntimeStatus.CANCELLED

        for node_id, state_str in context.task_states.items():
            if state_str in [TaskState.PENDING.value, TaskState.READY.value, TaskState.RUNNING.value]:
                context.task_states[node_id] = TaskState.CANCELLED.value
                cls.emit_event(
                    context,
                    RuntimeEventType.TASK_CANCELLED,
                    f"Task '{node_id}' CANCELLED by user request.",
                    node_id=node_id,
                )

        return context
