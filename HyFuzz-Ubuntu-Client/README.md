# HyFuzz Client (Ubuntu)

HyFuzz Client is the Linux-side execution agent for the HyFuzz distributed fuzzing platform. It receives
payloads from the Windows-based HyFuzz server, executes them inside hardened sandboxes, captures deep
instrumentation signals, and streams actionable results back to the control plane. The client targets
Ubuntu 22.04+ and is designed to run both on bare-metal hosts and within virtualised environments such
as VirtualBox or WSL.

> **Phase 3 status** – this repository contains the Phase 3 deliverables of the Ubuntu client. Major
> subsystems (targets, instrumentation, analysis, reporting, monitoring, scheduling, extended protocol
> support) are implemented and wired together for end-to-end fuzzing campaigns.

## Table of Contents

- [Key Capabilities](#key-capabilities)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Campaigns](#running-campaigns)
- [Directory Structure](#directory-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Further Documentation](#further-documentation)
- [Contributing](#contributing)
- [License](#license)

## Key Capabilities

- **Protocol-aware execution** – CoAP, Modbus, MQTT, HTTP, and gRPC handlers with protocol-specific
  payload shaping, validators, and vulnerability heuristics.
- **Distributed orchestration** – Receives tasks via MCP, schedules local workers, and supports
  distributed execution pools.
- **Hardened sandboxing** – Launches payloads through an extensible sandbox manager with cgroups,
  seccomp, namespaces, and optional QEMU/LXC isolation.
- **Instrumentation suite** – ptrace-based syscall monitoring, strace/ltrace parsing, coverage tracking,
  sanitizer log ingestion, and memory telemetry.
- **Crash & exploitability analysis** – Automatic triage, deduplication, exploitability scoring, and
  generation of succinct root-cause summaries.
- **Reporting & feedback** – Produces HTML/JSON/Markdown/CSV reports and pushes aggregated metrics
  back to the HyFuzz server for adaptive learning.
- **Operational monitoring** – Integrated metrics collector, resource monitor, alerting hooks, and
  health endpoints for fleet observability.

## Architecture Overview

The client is composed of several cooperating domains:

- **MCP Client** (`src/mcp_client/`) – maintains the transport session with the HyFuzz server, negotiates
  protocol support, and streams tasks/results.
- **Execution Core** (`src/execution/`) – orchestrates payload execution through the sandbox manager,
  tracks lifecycle events, and aggregates runtime data.
- **Targets Module** (`src/targets/`) – scans networks, fingerprints services, and resolves campaign
  scopes prior to fuzzing.
- **Instrumentation Layer** (`src/instrumentation/`) – attaches trace hooks, collects coverage, and
  persists low-level telemetry for later analysis.
- **Analysis Pipeline** (`src/analysis/`) – processes crash dumps, sanitizer reports, and generates
  exploitability insights using knowledge-driven heuristics.
- **Judge Integration** (`src/judge/`) – scores results locally, prepares feedback for the server-side
  LLM judge, and applies adaptive tuning instructions.
- **Reporting & Monitoring** (`src/reporting/`, `src/monitoring/`, `src/notifications/`) – converts raw
  execution data into human-readable artefacts and operational alerts.

A detailed component map is available in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Prerequisites

- Ubuntu 22.04 LTS (or newer) with Python 3.10+
- VirtualBox VM guest additions enabled when running inside macOS/Windows hosts
- Access to the HyFuzz server (MCP endpoint reachable over TCP/HTTP/WebSocket)
- Optional tooling:
  - `docker`/`podman` for containerised execution
  - `strace`, `ltrace`, `gdb`, `perf`, and sanitizers for extended instrumentation
  - `sqlite3` command-line tools for inspecting the local results database

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/hyfuzz-client-ubuntu.git
   cd hyfuzz-client-ubuntu
   ```
2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```
4. **Install optional tooling** (recommended)
   ```bash
   sudo apt install -y strace ltrace gdb clang lldb sqlite3 docker.io
   ```
5. **Initialise local data directories**
   ```bash
   make prepare
   ```

## Configuration

1. Copy the default environment template:
   ```bash
   cp config/.env.template .env
   ```
2. Edit `.env` to match your environment (server URL, authentication, sandbox paths).
3. Review YAML configuration bundles in `config/`:
   - `execution_config.yaml` – worker pools, timeouts, sandbox profiles
   - `instrumentation_config.yaml` – tracing plugins, sampling rates
   - `analysis_config.yaml` – crash classifiers, deduplication thresholds
   - `monitoring_config.yaml` – metrics exporters and alerting hooks
   - `notification_config.yaml` – Slack/email/webhook credentials
4. Example presets are provided under `config/example_configs/` for development, testing, aggressive,
   safe, protocol-specific, and distributed scenarios.

## Running Campaigns

- **Smoke test the connection**
  ```bash
  python scripts/test_connection.py --server http://SERVER_HOST:PORT
  ```
- **Run a quick protocol campaign**
  ```bash
  python scripts/run_coap_test.py --config config/example_configs/config_coap.yaml
  ```
- **Launch a full adaptive campaign**
  ```bash
  python scripts/run_campaign.py --config config/example_configs/config_dev.yaml
  ```
- **Monitor runtime metrics**
  ```bash
  python scripts/monitor_client.py
  ```
- **Generate reports after execution**
  ```bash
  python scripts/generate_report.py --format html --output data/reports/html/latest.html
  ```

Refer to [`docs/USAGE.md`](docs/USAGE.md) for end-to-end walkthroughs.

## Directory Structure

The most important directories are summarised below:

```
├── src/
│   ├── analysis/           # Crash & exploitability analysis pipeline
│   ├── execution/          # Orchestrator, sandbox manager, runtime monitors
│   ├── instrumentation/    # Coverage, ptrace, signal interception
│   ├── judge/              # Local scoring, adaptive feedback hooks
│   ├── mcp_client/         # Transports, protocol negotiation, session handling
│   ├── monitoring/         # Metrics collection, health checks, exporters
│   ├── notifications/      # Slack/email/webhook notifiers
│   ├── protocols/          # Protocol-specific handlers & fuzzers
│   ├── reporting/          # Report generators & templates
│   ├── targets/            # Discovery, profiling, fingerprinting
│   └── utils/              # Shared utilities and helpers
├── tests/                  # Unit, integration, performance, and e2e suites
├── scripts/                # Operational scripts for campaigns, monitoring, maintenance
├── docs/                   # Comprehensive documentation set
├── data/                   # Payload corpora, results, reports, SQLite DB
└── config/                 # Environment, execution, instrumentation, monitoring configs
```

## Development Workflow

1. **Run linters & type checks**
   ```bash
   make lint
   ```
2. **Execute the unit and integration suites**
   ```bash
   make test
   ```
3. **Start the client in development mode**
   ```bash
   python scripts/start_client.py --config config/example_configs/config_dev.yaml
   ```
4. **Iterate on protocols or instrumentation** – use notebooks in `notebooks/` to explore coverage,
   crash clusters, and metrics dashboards.

## Testing

- **Unit tests**
  ```bash
  pytest tests/unit
  ```
- **Integration tests**
  ```bash
  pytest tests/integration
  ```
- **Performance benchmarks**
  ```bash
  pytest tests/performance
  ```
- **End-to-end validation**
  ```bash
  pytest tests/e2e
  ```

## Troubleshooting

- Inspect logs in `logs/` (`execution.log`, `instrumentation.log`, `crash.log`, etc.).
- Use `python scripts/analyze_crashes.py` to inspect recent crash artefacts.
- Re-run `python scripts/health_check.sh` to verify sandbox prerequisites.
- Confirm connectivity to the HyFuzz server using `scripts/test_connection.py` and review firewall
  rules on both ends.
- Review [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for an extensive checklist.

## Further Documentation

The `docs/` directory contains focused guides on setup, architecture, instrumentation, target
management, crash analysis, monitoring, and deployment. Start with [`docs/README.md`](docs/README.md)
for the recommended reading order.

## Contributing

Contributions are welcome! Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) and open a pull request
with context about the scenario you are targeting. For significant changes, discuss them in an issue
first to align on goals and interfaces.

## License

HyFuzz Client is released under the MIT License. See [`LICENSE`](LICENSE) for details.
