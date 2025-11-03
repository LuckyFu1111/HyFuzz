"""Executes payloads in a controlled environment."""
from __future__ import annotations

from ..models.execution_models import ExecutionRequest, ExecutionResult
from ..protocols.protocol_factory import get_handler
from ..protocols.state_manager import get_state_manager
from ..utils.time_utils import utc_now


class PayloadExecutor:
    def execute(self, request: ExecutionRequest, state: "ExecutionState") -> ExecutionResult:
        handler = get_handler(request.protocol)
        capabilities = handler.get_capabilities()
        session_snapshot = None
        if request.session_id and capabilities.stateful:
            session = get_state_manager().get(request.protocol, request.session_id)
            response = handler.execute_stateful(request, session)
            session_snapshot = dict(session.attributes)
        else:
            response = handler.execute(request)
        diagnostics = {"timestamp": utc_now().isoformat(), "state": state.status}
        if session_snapshot is not None:
            diagnostics["session"] = session_snapshot
        return ExecutionResult(
            payload_id=request.payload_id,
            success=response.get("status") == "ok",
            output=response.get("message", ""),
            diagnostics=diagnostics,
            session_id=request.session_id,
        )


if __name__ == "__main__":
    from .execution_state import ExecutionState

    executor = PayloadExecutor()
    req = ExecutionRequest(payload_id="demo", protocol="coap")
    print(executor.execute(req, ExecutionState.current()))
