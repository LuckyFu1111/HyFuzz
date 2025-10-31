from src.protocols.modbus_handler import ModbusHandler
from src.models.execution_models import ExecutionRequest


def test_modbus_handler_executes():
    handler = ModbusHandler()
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="modbus"))
    assert response["status"] == "ok"
