#!/usr/bin/env python3
"""Execute a CoAP handler smoke test."""
from src.protocols.coap_handler import CoAPHandler
from src.models.execution_models import ExecutionRequest

if __name__ == "__main__":
    handler = CoAPHandler()
    print(handler.execute(ExecutionRequest(payload_id="demo", protocol="coap")))
