# Server Source Tree Overview

This directory contains the Windows HyFuzz server application code. The modules mirror the
architecture outlined in [`../README.md`](../README.md) and provide focused entry points for
LLM-driven fuzzing orchestration, defense intelligence, distributed scheduling, and observability.

## Module Map

| Package | Highlights |
| ------- | ---------- |
| `api/` | FastAPI/Starlette routes, HTTP/WebSocket transports, and middleware. |
| `auth/` | JWT/OAuth handlers, RBAC models, API key lifecycle, and session management. |
| `backup/` | Snapshot creation, restore helpers, incremental backup scheduler. |
| `cache/` | In-memory and distributed cache backends, eviction strategies, serialization helpers. |
| `config/` | Settings loader, environment handling, YAML templates, and validation utilities. |
| `dashboard/` | Real-time dashboard server, websocket handlers, static assets (JS/CSS/HTML). |
| `defense/` | Defense integrator, WAF/IDS parsers, evasion detector, defense feedback wiring. |
| `execution/` | Sandbox orchestration, signal capture, runtime monitoring, execution result models. |
| `fuzzing/` | Core fuzzing engine abstractions, payload handlers, and strategy registry. |
| `knowledge/` | Graph/vector DB access layers, knowledge fusion logic, CWE/CVE repositories. |
| `learning/` | Feedback loop, adaptive tuning, strategy optimizers, pattern analyzers. |
| `llm/` | LLM client/service wrappers, prompt builders, cache manager, judge implementation. |
| `mcp_server/` | MCP transports (stdio/HTTP/WebSocket), capability/session management, utilities. |
| `models/` | Pydantic/dataclass models for payloads, feedback, knowledge, configuration, and judging. |
| `monitoring/` | Metrics collectors, performance monitors, health checks, Prometheus exporter. |
| `notifications/` | Notifier interfaces, channel implementations (email/Slack/Discord/Teams/SMS). |
| `plugins/` | Plugin management framework, discovery, validation, and built-in extension points. |
| `protocols/` | Protocol registry, base classes, CoAP/Modbus/MQTT/HTTP/gRPC/JSON-RPC implementations. |
| `reporting/` | Report generation pipeline with PDF/HTML/JSON/CSV exporters and scheduling. |
| `resources/` | Rate limiting, quotas, resource allocation, connection pooling. |
| `scanning/` | Vulnerability scanning, pattern matching, CVE classifier integrations. |
| `tasks/` | Task queue abstractions, Celery app bootstrap, distributed worker orchestration. |
| `utils/` | Logging, exceptions, validation helpers, async utilities, metrics helpers. |

## Key Entry Points

- `__main__.py`: Allows `python -m src` to boot the MCP server in development environments.
- `mcp_server/server.py`: Primary server runner used by `scripts/start_server.py`.
- `llm/llm_judge.py`: Defense-aware judge that leverages graph + vector knowledge stores.
- `protocols/base_protocol.py`: Defines `ProtocolSpec` and `ProtocolSession`, enabling stateful vs.
  stateless campaign planning.

## Development Tips

1. Run `pytest` from the repository root to execute unit, integration, performance, and e2e suites.
2. Use the Makefile targets (`make lint`, `make test`, `make docs`) to align with CI expectations.
3. Update this README whenever you add a new package so downstream contributors can locate it quickly.
4. When registering new protocols, populate `ProtocolSpec` with the correct defaults/statefulness so
   the Ubuntu client can mirror the behaviour.

