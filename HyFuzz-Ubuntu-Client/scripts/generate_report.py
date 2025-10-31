#!/usr/bin/env python3
"""Generate a local JSON report."""
from src.reporting.json_reporter import JSONReporter
from src.reporting.report_generator import ReportGenerator

if __name__ == "__main__":
    generator = ReportGenerator()
    reporter = JSONReporter()
    data = generator.build_summary([{"payload_id": "1", "status": "ok"}])
    print(reporter.render(data))
