# Client Source Tree Overview

The Ubuntu client codebase lives here. It contains the execution agents, instrumentation pipelines,
analysis stack, and auxiliary services that cooperate with the Windows control plane.

## Module Map

| Package | Highlights |
| ------- | ---------- |
| `analysis/` | Crash/core dump analysis, exploitability scoring, deduplication workflows. |
| `config/` | Settings loader, environment templates, and preset YAML bundles. |
| `execution/` | Campaign orchestrator, payload executor, sandbox manager, runtime monitors. |
| `fuzzing/` | Optional extended fuzzing strategies (mutation, grammar, corpus/dictionary managers). |
| `integration/` | Bridges to third-party fuzzers (AFL, libFuzzer, Honggfuzz, Radamsa, Peach). |
| `instrumentation/` | ptrace/strace/ltrace handlers, coverage tracker, memory/syscall monitors. |
| `judge/` | Local scoring, metrics calculation, adaptive tuning, feedback integration. |
| `models/` | Pydantic/dataclass models for payloads, execution state, results, protocols, crashes. |
| `monitoring/` | System/resource/performance monitors, metrics collectors, health checks. |
| `mcp_client/` | Client transports (stdio/HTTP/WebSocket), connection management, heartbeat. |
| `notifications/` | Email/Slack/Webhook/console notifiers and formatting utilities. |
| `protocols/` | CoAP/Modbus/MQTT/HTTP/gRPC handlers, validators, packet parsers, fuzzing helpers. |
| `reporting/` | Report generators for HTML/JSON/Markdown/coverage/crash summaries. |
| `scheduling/` | Campaign manager, scheduler, task prioritiser, load balancer. |
| `storage/` | Database access layer, file storage, cache, archive helpers. |
| `targets/` | Target scanning, profiling, fingerprinting, vulnerability mapping. |
| `utils/` | Logging, exceptions, validators, helpers, async/system/process utilities. |

## Key Entry Points

- `__main__.py`: Enables `python -m src` to bootstrap the client orchestrator locally.
- `execution/orchestrator.py`: Coordinates payload execution flows and instrumentation hooks.
- `mcp_client/client.py`: Maintains the MCP session with the server.
- `protocols/base_handler.py`: Publishes `ProtocolCapabilities` so the coordinator can distinguish
  stateless and stateful handlers.

## Development Tips

1. Use `scripts/start_client.py` for an opinionated startup with logging and config wiring.
2. When adding a new protocol, update both `protocols/` and the server-side registry, then write
   integration coverage in `tests/integration/`.
3. Keep this README current whenever new packages appear so collaborators can navigate the tree
   quickly.
4. For stateful protocols mirror the server-side `ProtocolSpec` defaults inside
   `protocols/protocol_factory.py` so session-aware diagnostics stay aligned.

