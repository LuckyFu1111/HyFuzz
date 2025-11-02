from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests
from src.reporting.report_generator import ReportGenerator


def test_full_campaign_generates_report():
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["full"], "coap"))
    results = orchestrator.run()
    generator = ReportGenerator()
    summary = generator.build_summary([{ "payload_id": r.payload_id, "status": "ok" if r.success else "fail" } for r in results])
    assert summary[0]["payload_id"] == "full"
