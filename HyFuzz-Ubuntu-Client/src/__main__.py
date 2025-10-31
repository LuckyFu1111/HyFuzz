"""Entry point for running the client."""
from __future__ import annotations

from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def main() -> None:
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["demo"], "coap"))
    print(orchestrator.run())


if __name__ == "__main__":
    main()
