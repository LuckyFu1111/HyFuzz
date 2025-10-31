from src.protocols.mqtt_handler import MQTTHandler
from src.models.execution_models import ExecutionRequest


def test_mqtt_handler_executes():
    handler = MQTTHandler()
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="mqtt"))
    assert response["status"] == "ok"
