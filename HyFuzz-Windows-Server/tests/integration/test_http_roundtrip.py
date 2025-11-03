import asyncio
import aiohttp

from src.mcp_server.server import MCPServer, ServerConfig


def test_http_ping_roundtrip() -> None:
    async def runner() -> None:
        config = ServerConfig(
            host="127.0.0.1",
            port=0,
            transports=["http"],
            stdio_enabled=False,
            http_enabled=True,
            websocket_enabled=False,
        )
        server = MCPServer(config)
        await server.start()
        try:
            http_transport = server.transports["http"]
            sockets = http_transport.site._server.sockets  # type: ignore[attr-defined]
            port = sockets[0].getsockname()[1]

            payload = {"jsonrpc": "2.0", "method": "ping", "params": {}, "id": "test"}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"http://127.0.0.1:{port}/mcp/message", json=payload) as resp:
                    assert resp.status == 200
                    data = await resp.json()

            assert "error" not in data
            outer = data.get("result")
            assert isinstance(outer, dict)
            inner = outer.get("result")
            assert isinstance(inner, dict)
            assert inner.get("status") == "pong"
        finally:
            await server.stop()

    asyncio.run(runner())
