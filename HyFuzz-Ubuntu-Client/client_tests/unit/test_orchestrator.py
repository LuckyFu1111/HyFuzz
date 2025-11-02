from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_orchestrator_runs_requests():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["1"], "coap"))
    results = orchestrator.run()
    assert len(results) == 1
    assert results[0].success is True
