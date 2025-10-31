"""Execution orchestrator."""
from __future__ import annotations

from typing import Iterable, List

from .payload_executor import PayloadExecutor
from .result_collector import ResultCollector
from .crash_detector import CrashDetector
from .runtime_monitor import RuntimeMonitor
from .task_queue import TaskQueue
from .execution_state import ExecutionState
from ..models.execution_models import ExecutionRequest, ExecutionResult
from ..utils.logger import get_logger


class Orchestrator:
    def __init__(self) -> None:
        self.executor = PayloadExecutor()
        self.collector = ResultCollector()
        self.crash_detector = CrashDetector()
        self.runtime_monitor = RuntimeMonitor()
        self.task_queue = TaskQueue()
        self.logger = get_logger(__name__)

    def queue_requests(self, requests: Iterable[ExecutionRequest]) -> None:
        for request in requests:
            self.task_queue.enqueue(request)

    def run(self) -> List[ExecutionResult]:
        results: List[ExecutionResult] = []
        self.runtime_monitor.start()
        while not self.task_queue.empty:
            request = self.task_queue.dequeue()
            state = ExecutionState.current()
            result = self.executor.execute(request, state)
            self.collector.store(result)
            self.crash_detector.inspect(result)
            results.append(result)
        self.runtime_monitor.stop()
        return results


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.queue_requests([ExecutionRequest(payload_id="1", protocol="coap")])
    print(orchestrator.run())
