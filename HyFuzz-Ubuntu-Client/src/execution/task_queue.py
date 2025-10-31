"""Simple in-memory task queue."""
from __future__ import annotations

from collections import deque
from typing import Deque

from ..models.execution_models import ExecutionRequest


class TaskQueue:
    def __init__(self) -> None:
        self._queue: Deque[ExecutionRequest] = deque()

    def enqueue(self, request: ExecutionRequest) -> None:
        self._queue.append(request)

    def dequeue(self) -> ExecutionRequest:
        return self._queue.popleft()

    @property
    def empty(self) -> bool:
        return not self._queue


if __name__ == "__main__":
    from ..models.execution_models import ExecutionRequest

    q = TaskQueue()
    q.enqueue(ExecutionRequest(payload_id="1", protocol="coap"))
    print(q.dequeue())
