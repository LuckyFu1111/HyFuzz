#!/usr/bin/env python3
"""Test connectivity to the server."""
from src.mcp_client.client import MCPClient, ClientConfig

if __name__ == "__main__":
    client = MCPClient(ClientConfig(server_url="http://localhost", protocols=["coap"]))
    client.connect()
    print(client.send_payload({"payload_id": "ping", "protocol": "coap"}))
