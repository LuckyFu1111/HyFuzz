"""HyFuzz Windows MCP Server launcher.

This script boots the HyFuzz MCP server with the runtime configuration used
throughout Phase 3.  It performs a light-weight environment validation,
initialises the asynchronous server, and keeps the event loop alive until a
shutdown signal is received.  When executed with ``--smoke-test`` the launcher
starts an ephemeral HTTP transport and performs a JSON-RPC ``ping`` round-trip
so the client tooling can verify connectivity without manual steps.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mcp_server.server import MCPServer, ServerConfig as CoreServerConfig  # noqa: E402

TRANSPORT_CHOICES = {"stdio", "http", "websocket"}


@dataclass(slots=True)
class RuntimeConfig:
    """Runtime options supplied via the CLI."""

    host: str = "127.0.0.1"
    port: int = 8000
    transports: List[str] = field(default_factory=lambda: ["http"])
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_health_check: bool = True
    smoke_test: bool = False

    def to_core_config(self) -> CoreServerConfig:
        """Convert the runtime configuration to the core server dataclass."""

        transports = self.transports or ["stdio"]
        return CoreServerConfig(
            host=self.host,
            port=self.port,
            transports=transports,
            stdio_enabled="stdio" in transports,
            http_enabled="http" in transports,
            websocket_enabled="websocket" in transports,
            enable_metrics=self.enable_metrics,
        )


class LoggerSetup:
    """Helper for consistent logging configuration."""

    @staticmethod
    def setup_logging(level: str = "INFO") -> logging.Logger:
        log_path = PROJECT_ROOT / "logs" / "server.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_path, encoding="utf-8"),
            ],
        )
        logger = logging.getLogger("hyfuzz.server.launcher")
        logger.debug("Logging initialised at %s", level.upper())
        return logger


class EnvironmentValidator:
    """Very small set of health checks prior to server startup."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def validate(self) -> None:
        self._ensure_directories("src", "config", "logs")
        self.logger.info("Environment validation complete")

    def _ensure_directories(self, *relative_paths: str) -> None:
        for rel in relative_paths:
            path = PROJECT_ROOT / rel
            if not path.exists():
                raise FileNotFoundError(f"Required directory missing: {path}")
            self.logger.debug("✓ %s", path)


class MCPServerManager:
    """Wrapper around :class:`MCPServer` that exposes high level helpers."""

    def __init__(self, logger: logging.Logger, config: RuntimeConfig):
        self.logger = logger
        self.config = config
        self.server: Optional[MCPServer] = None
        self._shutdown_waiter: Optional[asyncio.Task[None]] = None
        self.is_running = False

    async def start(self) -> None:
        if self.server is None:
            core_config = self.config.to_core_config()
            self.server = MCPServer(core_config)
            self.logger.debug("Initialised MCPServer with transports %s", core_config.transports)

        await self.server.start()
        self.is_running = True
        self._shutdown_waiter = asyncio.create_task(self.server.shutdown_event.wait())
        self.logger.info(
            "MCP server running (transports=%s)", ",".join(self.server.config.transports)
        )

    async def stop(self) -> None:
        if not self.server:
            return

        await self.server.stop()
        if self._shutdown_waiter and not self._shutdown_waiter.done():
            await self._shutdown_waiter
        self._shutdown_waiter = None
        self.is_running = False
        self.logger.info("MCP server stopped")

    async def wait_until_stopped(self) -> None:
        if self._shutdown_waiter:
            await self._shutdown_waiter

    async def health_check(self) -> dict[str, object]:
        if not self.server:
            return {"status": "uninitialised"}
        return await self.server.health_check()

    def resolved_port(self) -> int:
        if not self.server:
            return self.config.port

        http_transport = self.server.transports.get("http")
        if http_transport and getattr(http_transport, "site", None):
            site = http_transport.site
            if site and site._server and site._server.sockets:  # type: ignore[attr-defined]
                return site._server.sockets[0].getsockname()[1]
        return self.config.port


class ServerRunner:
    """Coordinates validation, startup, monitoring, and shutdown."""

    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.logger = LoggerSetup.setup_logging(config.log_level)
        self.manager = MCPServerManager(self.logger, config)

    async def run(self) -> int:
        try:
            EnvironmentValidator(self.logger).validate()
            await self.manager.start()
            if self.config.enable_health_check:
                health = await self.manager.health_check()
                self.logger.info("Initial health check: %s", health["status"])
            self.logger.info(
                "Listening on %s:%s", self.config.host, self.manager.resolved_port()
            )
            await self._wait_for_shutdown()
            await self.manager.stop()
            return 0
        except Exception:  # pragma: no cover - defensive logging
            self.logger.exception("Server runner aborted due to an unrecoverable error")
            await self.manager.stop()
            return 1

    async def _wait_for_shutdown(self) -> None:
        loop = asyncio.get_running_loop()
        shutdown_event = asyncio.Event()

        def _signal_handler(signum: int, _frame: Optional[object]) -> None:
            self.logger.info("Received signal %s, shutting down", signal.Signals(signum).name)
            shutdown_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _signal_handler, sig, None)
            except NotImplementedError:  # pragma: no cover - Windows fallback
                signal.signal(sig, lambda s, f: _signal_handler(s, f))

        await asyncio.wait(
            [shutdown_event.wait(), self.manager.wait_until_stopped()],
            return_when=asyncio.FIRST_COMPLETED,
        )


async def _run_smoke_test(config: RuntimeConfig) -> bool:
    """Start an ephemeral HTTP transport and issue a ping request."""

    smoke_config = RuntimeConfig(
        host=config.host,
        port=0,
        transports=["http"],
        log_level="WARNING",
    )
    manager = MCPServerManager(logging.getLogger("hyfuzz.smoke"), smoke_config)
    await manager.start()
    try:
        import aiohttp

        port = manager.resolved_port()
        async with aiohttp.ClientSession() as session:
            payload = {"jsonrpc": "2.0", "method": "ping", "params": {}, "id": "smoke"}
            url = f"http://{smoke_config.host}:{port}/mcp/message"
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
        return data["result"]["status"] == "pong"
    finally:
        await manager.stop()


def _normalise_transports(raw: Iterable[str]) -> List[str]:
    transports: List[str] = []
    for entry in raw:
        for token in entry.split(","):
            token = token.strip().lower()
            if not token:
                continue
            if token not in TRANSPORT_CHOICES:
                raise ValueError(f"Unsupported transport '{token}'")
            transports.append(token)
    return transports or ["stdio"]


def parse_arguments(argv: Optional[Iterable[str]] = None) -> RuntimeConfig:
    parser = argparse.ArgumentParser(description="HyFuzz MCP server launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument(
        "--transport",
        action="append",
        default=["http"],
        help="Comma separated transport list (stdio,http,websocket)",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument(
        "--disable-metrics", action="store_true", help="Disable metrics collection"
    )
    parser.add_argument(
        "--disable-health-check",
        action="store_true",
        help="Skip the startup health probe",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run an ephemeral server and exit after a ping round-trip",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    transports = _normalise_transports(args.transport)
    return RuntimeConfig(
        host=args.host,
        port=args.port,
        transports=transports,
        log_level=args.log_level,
        enable_metrics=not args.disable_metrics,
        enable_health_check=not args.disable_health_check,
        smoke_test=args.smoke_test,
    )


async def main(argv: Optional[Iterable[str]] = None) -> int:
    config = parse_arguments(argv)

    if config.smoke_test:
        success = await _run_smoke_test(config)
        print("Smoke test:", "passed" if success else "failed")
        return 0 if success else 1

    runner = ServerRunner(config)
    return await runner.run()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
