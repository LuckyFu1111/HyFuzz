from unittest.mock import MagicMock

from src.mcp_client.connection_manager import ConnectionManager


def test_connection_manager_performs_health_and_initialize():
    session = MagicMock()
    health_response = MagicMock(status_code=200)
    init_response = MagicMock(status_code=200)
    health_response.raise_for_status.return_value = None
    init_response.raise_for_status.return_value = None
    init_response.json.return_value = {"jsonrpc": "2.0", "result": {}}
    session.get.return_value = health_response
    session.post.return_value = init_response

    manager = ConnectionManager("http://localhost:8000", session=session)
    handshake = manager.connect()

    assert handshake["jsonrpc"] == "2.0"
    assert manager.is_connected()
    session.get.assert_called_once_with("http://localhost:8000/health", timeout=5.0)
    session.post.assert_called_once()
