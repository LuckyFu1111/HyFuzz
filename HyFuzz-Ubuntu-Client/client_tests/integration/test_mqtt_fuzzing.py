from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_mqtt_fuzzing_flow():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["mqtt-1"], "mqtt"))
    results = orchestrator.run()
    assert results[0].success
