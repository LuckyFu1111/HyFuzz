from time import perf_counter

from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_execution_perf_under_threshold():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["1"], "coap"))
    start = perf_counter()
    orchestrator.run()
    duration = perf_counter() - start
    assert duration < 1.0
