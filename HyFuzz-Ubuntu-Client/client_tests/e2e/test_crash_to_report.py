from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests
from src.reporting.crash_report import CrashReport


def test_crash_to_report_pipeline():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["1"], "coap"))
    results = orchestrator.run()
    report = CrashReport().build({"payload_id": results[0].payload_id, "reason": "none"})
    assert "Crash" in report
