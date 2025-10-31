#!/usr/bin/env python3
"""Execute a Modbus handler smoke test."""
from src.protocols.modbus_handler import ModbusHandler
from src.models.execution_models import ExecutionRequest

if __name__ == "__main__":
    handler = ModbusHandler()
    print(handler.execute(ExecutionRequest(payload_id="demo", protocol="modbus")))
