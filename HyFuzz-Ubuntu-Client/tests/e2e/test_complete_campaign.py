from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_complete_campaign():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["a", "b"], "coap"))
    results = orchestrator.run()
    assert len(results) == 2
