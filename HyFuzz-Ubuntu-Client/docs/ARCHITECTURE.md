# Architecture

The HyFuzz Ubuntu client is composed of loosely coupled domains that collaborate to execute fuzzing
campaigns delivered by the Windows-based HyFuzz server. This document summarises each subsystem and the
primary data flows between them.

## High-Level Flow

```
Targets → Protocols → Execution → Instrumentation → Analysis → Reporting
                               ↘            ↘            ↘
                                MCP Client → Judge → Monitoring/Notifications
```

1. **Targets** discover and profile candidate endpoints.
2. **Protocols** construct campaign-specific payloads and validators.
3. **Execution** schedules payloads, manages sandboxes, and tracks runtime state.
4. **Instrumentation** collects telemetry during execution (syscalls, coverage, sanitizer output).
5. **Analysis** triages failures, deduplicates crashes, and evaluates exploitability.
6. **Reporting** & **Notifications** package findings for humans and upstream systems.
7. **Judge** produces feedback to tune subsequent payload batches.
8. **MCP Client** synchronises with the server, exchanging payloads, results, and metadata.

## Subsystems

### MCP Client (`src/mcp_client/`)

- Supports stdio, HTTP, and WebSocket transports.
- Negotiates supported protocols using `protocol_selector.py`.
- Maintains liveliness with `heartbeat_manager.py` and retries via `retry_handler.py`.
- Persists connection metadata so campaigns can resume after transient failures.

### Execution Core (`src/execution/`)

- `orchestrator.py` coordinates worker threads/processes and dispatches payloads from the task queue.
- `payload_executor.py` launches binaries or network interactions inside sandbox profiles defined in
  `sandbox_manager.py`.
- `resource_monitor.py`, `timeout_manager.py`, and `signal_handler.py` provide guardrails to prevent host
  exhaustion.
- Execution results are normalised into `models/execution_models.py` before further processing.

### Protocol Adapters (`src/protocols/`)

- Each handler derives from `base_handler.py` and focuses on a single protocol (CoAP, Modbus, MQTT,
  HTTP, gRPC).
- `protocol_factory.py` instantiates handlers based on campaign metadata supplied by the server.
- `payload_generator.py` and `fuzz_engine.py` cooperate to mutate seeds, respecting protocol grammars.
- Validators and vulnerability heuristics reside in `*_vulnerabilities.py` modules to keep logic modular.

### Target Intelligence (`src/targets/`)

- `target_scanner.py` performs service discovery and stores assets in the SQLite cache.
- `service_detector.py` and `version_fingerprint.py` enrich targets with banner and fingerprint details.
- `vulnerability_mapper.py` aligns detected versions with known CVEs for prioritisation.
- Targets are shared with the server to support coordinated campaign planning.

### Instrumentation Layer (`src/instrumentation/`)

- `instrumentor.py` activates tracers (`ptrace_handler.py`, `strace_parser.py`, `ltrace_parser.py`).
- `coverage_tracker.py` computes basic block and edge coverage, emitting LCOV-compatible artefacts.
- `memory_tracker.py` captures allocator stats, while `syscall_monitor.py` tracks syscall sequences.
- `signal_interceptor.py` forwards crash signals to the analysis subsystem in real time.

### Analysis Pipeline (`src/analysis/`)

- `crash_analyzer.py` ingests crash reports, correlates instrumentation output, and groups similar
  failures.
- `core_dump_analyzer.py` extracts stack traces and register state from generated core dumps.
- `asan_parser.py` and `valgrind_parser.py` normalise sanitizer output into structured findings.
- `exploitability_checker.py` estimates risk levels, feeding results into `deduplicator.py` to prevent
  duplicate tickets.

### Judge & Feedback (`src/judge/`)

- Local judge calculates metrics via `metrics_calculator.py`, `coverage_analyzer.py`, and
  `crash_analyzer.py` (for severity hints).
- Results are serialised into `models/result_models.py` before being sent to the server-side LLM judge.
- Adaptive tuning instructions from the server are applied through `adaptive_tuner.py` and propagated
  back to the execution core.

### Reporting & Monitoring (`src/reporting/`, `src/monitoring/`, `src/notifications/`)

- Report generator exports campaign summaries (`report_generator.py`, `crash_report.py`,
  `coverage_report.py`).
- Monitoring subsystem polls host metrics, integrates with Prometheus exporters, and triggers alerts via
  notifiers (email, Slack, webhook).
- Notifications use `notification_models.py` to unify message formatting.

### Storage (`src/storage/`)

- `database.py` manages the SQLite database located in `data/database/client.db`.
- `result_archiver.py` rotates historical artefacts into `data/results/`.
- `crash_storage.py` maintains reproducible crash inputs for re-analysis.

## Data Stores

| Store | Location | Purpose |
|-------|----------|---------|
| Environment | `.env`, `config/` | Runtime parameters, secrets, and presets |
| Results DB | `data/database/client.db` | Execution metadata, targets, crash catalogue |
| Payload corpora | `data/payloads/` | Seeds, dictionaries, protocol-specific payloads |
| Reports | `data/reports/` | Generated HTML/JSON/Markdown/CSV artefacts |
| Logs | `logs/` | Component-specific log files with rotation support |

## Extensibility Points

- **New protocol** – implement a handler in `src/protocols/`, register it in `protocol_factory.py`, and
  add fixtures/tests under `client_tests/`.
- **Custom instrumentation** – extend `instrumentor.py` with a plugin that conforms to the existing
  interface; reference it from `instrumentation_config.yaml`.
- **Alternative storage** – swap the repository implementation in `src/storage/` to integrate remote
  databases or object stores.
- **Alert destinations** – add notifier adapters under `src/notifications/` for tools like Teams or
  PagerDuty.

## Observability

- All subsystems emit structured logs using `src/utils/logger.py` with correlation IDs.
- Metrics are exposed through the monitoring subsystem and can be scraped by Prometheus or shipped to
  the HyFuzz server.
- Coverage artefacts are stored in LCOV format and can be visualised via the notebooks or lcov viewers.

Refer to [`docs/USAGE.md`](USAGE.md) for a day-to-day workflow and [`docs/REPORTING_GUIDE.md`](REPORTING_GUIDE.md)
for post-processing outputs.
