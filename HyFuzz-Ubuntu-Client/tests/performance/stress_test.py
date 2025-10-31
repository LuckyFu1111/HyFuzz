from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_stress_runs_multiple_requests():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests([str(i) for i in range(5)], "coap"))
    results = orchestrator.run()
    assert len(results) == 5
