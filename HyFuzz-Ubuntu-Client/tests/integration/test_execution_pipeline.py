from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_execution_pipeline_returns_results():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["pipeline"], "coap"))
    results = orchestrator.run()
    assert results and results[0].payload_id == "pipeline"
