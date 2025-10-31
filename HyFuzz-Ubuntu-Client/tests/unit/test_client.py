from unittest.mock import MagicMock

from src.mcp_client.client import MCPClient, ClientConfig


def test_client_heartbeat_and_protocol_selection():
    client = MCPClient(
        ClientConfig(server_url="http://localhost", protocols=["coap", "modbus"])
    )

    mock_manager = MagicMock()
    mock_manager.connect.return_value = {"result": {"protocolVersion": "demo"}}
    mock_manager.send.return_value = {
        "jsonrpc": "2.0",
        "result": {"name": "coap_fuzz", "result": {}},
    }
    client.connection_manager = mock_manager

    client.connect()
    response = client.send_payload({"payload_id": "test", "protocol": "coap"})

    assert response["result"]["name"] == "coap_fuzz"
    sent_message = mock_manager.send.call_args[0][0]
    assert sent_message["method"] == "tools/call"
    assert sent_message["params"]["arguments"]["protocol"] == "coap"
    assert client.is_alive()
