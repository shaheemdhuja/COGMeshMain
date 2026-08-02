"""In-memory FIFO ExecutionQueue for scheduled TaskAssignments."""

from collections import deque
from typing import Optional
from app.scheduler.assignment import TaskAssignment


class ExecutionQueue:
    """In-memory FIFO queue holding ready-to-execute TaskAssignments."""

    def __init__(self) -> None:
        """Initialize empty deque."""
        self._queue: deque[TaskAssignment] = deque()

    def enqueue(self, assignment: TaskAssignment) -> None:
        """Add a TaskAssignment to the back of the queue (FIFO)."""
        self._queue.append(assignment)

    def dequeue(self) -> Optional[TaskAssignment]:
        """Pop the oldest TaskAssignment from the front of the queue, or None if empty."""
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Return count of items currently in queue."""
        return len(self._queue)

    def clear(self) -> None:
        """Purge all assignments from queue."""
        self._queue.clear()
