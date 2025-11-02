from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_modbus_fuzzing_flow():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["modbus-1"], "modbus"))
    results = orchestrator.run()
    assert results[0].success
