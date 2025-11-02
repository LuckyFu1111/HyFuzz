from src.protocols.http_handler import HTTPHandler
from src.models.execution_models import ExecutionRequest


def test_http_handler_executes():
    handler = HTTPHandler()
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="http"))
    assert response["status"] == "ok"
