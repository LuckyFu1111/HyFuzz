"""Modbus protocol handler."""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler, ProtocolCapabilities
from .state_manager import ProtocolSessionState
from ..models.execution_models import ExecutionRequest


class ModbusHandler(BaseProtocolHandler):
    name = "modbus"
    capabilities = ProtocolCapabilities(
        name="modbus",
        description="Modbus handler with session tracking",
        stateful=True,
        default_parameters={"function_code": "3", "address": "0", "count": "1"},
    )

    def _simulate(self, request: ExecutionRequest) -> Dict[str, str]:
        function_code_raw = request.parameters.get("function_code", "3")
        address_raw = request.parameters.get("address", "0")
        count_raw = request.parameters.get("count", "1")

        try:
            function_code = int(function_code_raw)
            address = int(address_raw)
            count = int(count_raw)
        except (TypeError, ValueError):
            return {
                "status": "error",
                "message": "Invalid Modbus parameters",
                "function_code": -1,
                "address": -1,
                "count": -1,
                "success": False,
            }

        valid_function_codes = {1, 2, 3, 4}
        success = function_code in valid_function_codes and count > 0
        status = "ok" if success else "error"
        message = (
            f"Modbus fc={function_code} addr={address} count={count} -> {request.payload_id}"
        )
        if not success:
            message += " rejected"
        return {
            "status": status,
            "message": message,
            "function_code": function_code,
            "address": address,
            "count": count,
            "success": success,
        }

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        simulated = self._simulate(request)
        return {"status": simulated["status"], "message": simulated["message"]}

    def execute_stateful(
        self, request: ExecutionRequest, session: ProtocolSessionState
    ) -> Dict[str, str]:
        simulated = self._simulate(request)
        history = session.attributes.setdefault("history", [])
        history.append(
            {
                "function_code": simulated["function_code"],
                "address": simulated["address"],
                "count": simulated["count"],
                "success": simulated["success"],
            }
        )
        session.attributes["request_count"] = len(history)
        return {"status": simulated["status"], "message": simulated["message"]}


if __name__ == "__main__":
    sample = ExecutionRequest(
        payload_id="1",
        protocol="modbus",
        parameters={"function_code": "3", "address": "0", "count": "1"},
    )
    print(ModbusHandler().execute(sample))
