from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_coap_fuzzing_flow():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["coap-1"], "coap"))
    results = orchestrator.run()
    assert results[0].success
