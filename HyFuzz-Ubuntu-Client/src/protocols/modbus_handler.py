"""Modbus protocol handler."""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler
from ..models.execution_models import ExecutionRequest


class ModbusHandler(BaseProtocolHandler):
    name = "modbus"

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        function_code_raw = request.parameters.get("function_code", "3")
        address_raw = request.parameters.get("address", "0")
        count_raw = request.parameters.get("count", "1")

        try:
            function_code = int(function_code_raw)
            address = int(address_raw)
            count = int(count_raw)
        except (TypeError, ValueError):
            return {"status": "error", "message": "Invalid Modbus parameters"}

        valid_function_codes = {1, 2, 3, 4}
        success = function_code in valid_function_codes and count > 0
        status = "ok" if success else "error"
        message = (
            f"Modbus fc={function_code} addr={address} count={count} -> {request.payload_id}"
        )
        if not success:
            message += " rejected"
        return {"status": status, "message": message}


if __name__ == "__main__":
    sample = ExecutionRequest(
        payload_id="1",
        protocol="modbus",
        parameters={"function_code": "3", "address": "0", "count": "1"},
    )
    print(ModbusHandler().execute(sample))
