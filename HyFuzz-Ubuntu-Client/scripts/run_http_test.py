#!/usr/bin/env python3
"""Run a quick HTTP handler test."""
from src.protocols.http_handler import HTTPHandler
from src.models.execution_models import ExecutionRequest

if __name__ == "__main__":
    handler = HTTPHandler()
    result = handler.execute(ExecutionRequest(payload_id="http-demo", protocol="http"))
    print(result)
