from src.protocols.modbus_handler import ModbusHandler
from src.models.execution_models import ExecutionRequest
from src.protocols.state_manager import ProtocolSessionState


def test_modbus_handler_executes():
    handler = ModbusHandler()
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="modbus"))
    assert response["status"] == "ok"


def test_modbus_handler_tracks_state():
    handler = ModbusHandler()
    session = ProtocolSessionState(session_id="demo")
    request = ExecutionRequest(
        payload_id="1",
        protocol="modbus",
        parameters={"function_code": "3", "address": "2", "count": "1"},
        session_id="demo",
    )
    handler.execute_stateful(request, session)
    assert session.attributes["request_count"] == 1
    assert session.attributes["history"][0]["function_code"] == 3
