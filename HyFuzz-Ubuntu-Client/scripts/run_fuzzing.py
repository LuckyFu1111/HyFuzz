#!/usr/bin/env python3
"""Run a simple fuzzing loop."""
from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["demo"], "coap"))
    print(orchestrator.run())
