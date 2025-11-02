# Monitoring Guide

The monitoring subsystem provides situational awareness for client health, performance, and resource
utilisation during fuzzing campaigns.

## Components

| Module | Purpose |
|--------|---------|
| `src/monitoring/system_monitor.py` | CPU, memory, disk, and network sampling |
| `src/monitoring/performance_monitor.py` | Tracks execution throughput, queue depth, latency |
| `src/monitoring/resource_monitor.py` | Observes sandbox cgroup statistics |
| `src/monitoring/metrics_collector.py` | Normalises metrics and exposes exporters |
| `src/monitoring/health_checker.py` | Aggregates health status, integrates with notifiers |
| `src/monitoring/monitoring_models.py` | Typed models for metrics and alerts |

## Usage

Start the monitoring loop:

```bash
python scripts/monitor_client.py --interval 30 --push
```

Flags:

- `--push` – send metrics to the server via MCP.
- `--export prometheus` – expose `/metrics` endpoint for Prometheus scraping.
- `--alert-on degraded` – trigger alerts when health status changes to `degraded` or `critical`.

## Metrics Catalog

| Metric | Description |
|--------|-------------|
| `hyfuzz_cpu_percent` | CPU utilisation of client process group |
| `hyfuzz_memory_bytes` | Resident memory usage |
| `hyfuzz_queue_depth` | Pending payloads in execution queue |
| `hyfuzz_execution_throughput` | Payloads processed per minute |
| `hyfuzz_crash_rate` | Crashes detected per hour |
| `hyfuzz_protocol_latency_seconds` | Average round-trip latency per protocol |

Additional metrics can be registered via `metrics_collector.py` plugin interface.

## Alerting

Configure alert destinations in `config/notification_config.yaml` (email, Slack, webhook). Example Slack
snippet:

```yaml
slack:
  enabled: true
  webhook_url: https://hooks.slack.com/services/TOKEN
  channels:
    - "#hyfuzz-alerts"
  severity_threshold: warning
```

Health checker classifications:

- `healthy` – All metrics within thresholds.
- `warning` – Minor resource pressure or elevated error counts.
- `degraded` – Sustained issues; alerts triggered.
- `critical` – Immediate attention required; consider pausing campaigns.

## Dashboards

- Use `notebooks/05_metrics_dashboard.ipynb` to build ad-hoc dashboards from captured metrics.
- Export Prometheus data to Grafana using `docker/prometheus_exporter.py` (if configured).

## Maintenance

- Rotate monitoring logs with `scripts/maintenance/rotate_logs.sh`.
- Review metric definitions periodically to ensure they align with SLAs.
- Validate monitoring functionality with:
  ```bash
  pytest client_tests/unit/test_monitoring.py
  pytest client_tests/performance/test_instrumentation_perf.py -k monitor
  ```

For integration with reporting workflows, see [`REPORTING_GUIDE.md`](REPORTING_GUIDE.md). For operational
playbooks, consult [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
