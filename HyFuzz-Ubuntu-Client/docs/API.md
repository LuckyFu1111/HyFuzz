# Client API Reference

The HyFuzz client exposes a lightweight API surface through its orchestration layer and MCP interface.
This document summarises the key entry points for automation.

## Python Entry Points

Most programmatic control happens via Python modules under `src/`.

| Module | Functionality |
|--------|---------------|
| `src/execution/orchestrator.py` | `run_campaign(config_path, options)` to start campaigns programmatically |
| `src/mcp_client/client.py` | `MCPClient` class for connecting to the server and streaming payloads |
| `src/judge/judge.py` | `Judge` class for scoring results and generating feedback |
| `src/reporting/report_generator.py` | `ReportGenerator` for producing artefacts |
| `src/monitoring/metrics_collector.py` | `MetricsCollector` for custom metric registration |

Import these modules in your own tooling after activating the repository virtual environment.

## CLI Scripts

Scripts under `scripts/` wrap the Python API for ease of use. Examples:

```bash
python scripts/run_campaign.py --config config/example_configs/config_dev.yaml
python scripts/generate_report.py --format html --output data/reports/html/report.html
python scripts/analyze_crashes.py --list --limit 5
```

Run `python <script> --help` for full argument lists.

## MCP Endpoints

The client communicates with the server via Model Context Protocol transports. The core messages include:

| Direction | Message | Description |
|-----------|---------|-------------|
| Client → Server | `client.register` | Advertise supported protocols, capabilities, and client metadata |
| Client → Server | `client.results` | Submit execution outcomes, crashes, and metrics |
| Server → Client | `server.payload` | Deliver payload batches for execution |
| Server → Client | `server.feedback` | Provide adaptive tuning instructions |
| Bidirectional | `heartbeat` | Maintain session liveliness |

Transport configuration (HTTP, stdio, WebSocket) is handled by `src/mcp_client/http_transport.py`,
`stdio_transport.py`, and `websocket_transport.py`.

## Database Access

Data is persisted in `data/database/client.db` (SQLite). Access through `src/storage/database.py`:

```python
from src.storage.database import Database

db = Database("data/database/client.db")
with db.session_scope() as session:
    recent = session.get_recent_executions(limit=10)
```

Use read-only queries when integrating with external dashboards to avoid locking the database during
campaigns.

## Extending the API

- Add new scripts under `scripts/` that wrap orchestration functions.
- Expose additional MCP capabilities by updating `src/mcp_client/capabilities.py` (if present) and the
  server counterpart.
- Introduce REST/gRPC endpoints by integrating with `src/api/` (planned) or embedding FastAPI inside the
  client if remote control is required.

For detailed usage examples, inspect tests in `tests/integration/` and notebooks under `notebooks/`.
