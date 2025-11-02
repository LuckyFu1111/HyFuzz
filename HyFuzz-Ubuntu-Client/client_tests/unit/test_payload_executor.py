from src.execution.payload_executor import PayloadExecutor
from src.execution.execution_state import ExecutionState
from src.models.execution_models import ExecutionRequest


def test_payload_executor_returns_success():
    executor = PayloadExecutor()
    result = executor.execute(ExecutionRequest(payload_id="1", protocol="coap"), ExecutionState.current())
    assert result.success is True
