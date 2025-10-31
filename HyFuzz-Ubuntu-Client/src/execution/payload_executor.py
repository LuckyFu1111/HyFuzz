"""Executes payloads in a controlled environment."""
from __future__ import annotations

from ..models.execution_models import ExecutionRequest, ExecutionResult
from ..protocols.protocol_factory import get_handler
from ..utils.time_utils import utc_now


class PayloadExecutor:
    def execute(self, request: ExecutionRequest, state: "ExecutionState") -> ExecutionResult:
        handler = get_handler(request.protocol)
        response = handler.execute(request)
        diagnostics = {"timestamp": utc_now().isoformat(), "state": state.status}
        return ExecutionResult(
            payload_id=request.payload_id,
            success=response.get("status") == "ok",
            output=response.get("message", ""),
            diagnostics=diagnostics,
        )


if __name__ == "__main__":
    from .execution_state import ExecutionState

    executor = PayloadExecutor()
    req = ExecutionRequest(payload_id="demo", protocol="coap")
    print(executor.execute(req, ExecutionState.current()))
