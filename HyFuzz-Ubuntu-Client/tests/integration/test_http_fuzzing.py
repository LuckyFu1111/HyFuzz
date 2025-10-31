from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_http_fuzzing_flow():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["http-1"], "http"))
    results = orchestrator.run()
    assert results[0].success
