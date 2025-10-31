# Setup Guide

This guide walks through installing, configuring, and validating the HyFuzz Ubuntu client on a fresh
machine or virtual machine (VirtualBox, VMware, or cloud instance).

## 1. System Preparation

1. Update the system and install base packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y build-essential python3 python3-venv python3-pip git
   ```
2. (Optional) Install instrumentation tools:
   ```bash
   sudo apt install -y strace ltrace gdb clang llvm lldb valgrind perf sqlite3
   ```
3. Enable core dumps if you plan to run crash analysis:
   ```bash
   echo "* hard core unlimited" | sudo tee -a /etc/security/limits.conf
   sudo sysctl -w kernel.core_pattern=/tmp/core.%e.%p.%t
   ```
4. Inside VirtualBox, ensure Guest Additions are installed for shared folders and clipboard support.

## 2. Repository Checkout

```bash
git clone https://github.com/your-org/hyfuzz-client-ubuntu.git
cd hyfuzz-client-ubuntu
```

If you are syncing from another host (e.g., macOS development machine), ensure timestamps are preserved
to avoid unnecessary rebuilds.

## 3. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Use `requirements.txt` instead when provisioning a lightweight runtime without developer tooling.

## 4. Environment Variables

1. Copy the template and customise values:
   ```bash
   cp config/.env.template .env
   ```
2. Edit `.env` to set:
   - `MCP_ENDPOINT` – URL/host of the HyFuzz server
   - `AUTH_MODE` and `API_KEY`/`TOKEN` if authentication is enabled
   - `SANDBOX_ROOT` – directory used for sandbox chroots or overlay filesystems
   - `LOG_LEVEL` – INFO (default) or DEBUG for verbose output

## 5. Configuration Bundles

The client uses layered YAML files located in `config/`.

| File | Description |
|------|-------------|
| `execution_config.yaml` | Worker pools, concurrency, timeouts, sandbox profiles |
| `protocol_config.yaml` | Per-protocol limits, payload mutators, validators |
| `sandbox_config.yaml` | Namespace settings, seccomp profiles, mount options |
| `instrumentation_config.yaml` | Tracers to enable (ptrace, coverage, sanitizers) |
| `analysis_config.yaml` | Crash triage thresholds, deduplication heuristics |
| `monitoring_config.yaml` | Metrics exporters, health intervals, Prometheus settings |
| `notification_config.yaml` | Slack/email/webhook destinations |

Preset bundles in `config/example_configs/` demonstrate typical deployment scenarios (development,
aggressive fuzzing, safe fuzzing, protocol-specific campaigns, distributed execution).

## 6. Data Directory Initialisation

```bash
make prepare
```

This target creates the required directory tree under `data/` and `logs/`, seeds the SQLite database, and
copies example corpora if they do not already exist.

## 7. Connectivity Check

```bash
python scripts/test_connection.py --server http://SERVER_HOST:PORT
```

If the server enforces TLS or authentication, add the corresponding flags shown in the script help
(`-h`).

## 8. Health Validation

Run the health checks before joining a distributed campaign:

```bash
python scripts/monitor_client.py --once
python scripts/health_check.sh
pytest tests/unit -k "monitoring or sandbox"
```

Ensure `logs/monitoring.log` and `logs/sandbox.log` report no errors.

## 9. Optional: Docker-Based Setup

1. Build the image:
   ```bash
   docker build -f docker/client.dockerfile -t hyfuzz-client .
   ```
2. Run the container:
   ```bash
   docker run --rm -it \
     --net host \
     -v "$PWD/data:/app/data" \
     -v "$PWD/logs:/app/logs" \
     --env-file .env \
     hyfuzz-client
   ```
3. Use the same scripts inside the container (`python scripts/run_campaign.py ...`).

## 10. Next Steps

- Follow [`USAGE.md`](USAGE.md) to launch campaigns.
- Review [`INSTRUMENTATION.md`](INSTRUMENTATION.md) to enable advanced telemetry.
- Explore [`REPORTING_GUIDE.md`](REPORTING_GUIDE.md) for exporting campaign summaries.
