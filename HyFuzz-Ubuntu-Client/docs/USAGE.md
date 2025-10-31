# Usage Guide

This guide covers daily workflows for operating the HyFuzz Ubuntu client once it has been installed and
configured.

## Campaign Lifecycle

1. **Synchronise targets**
   ```bash
   python scripts/targets/scan_targets.py --network 10.0.0.0/24
   python scripts/targets/profile_target.py --target-id TARGET_UUID
   ```
2. **Start the client**
   ```bash
   python scripts/start_client.py --config config/example_configs/config_dev.yaml
   ```
3. **Monitor execution**
   - Tail logs (`tail -f logs/execution.log logs/instrumentation.log`)
   - Stream metrics (`python scripts/monitor_client.py`)
4. **Review results**
   ```bash
   sqlite3 data/database/client.db 'SELECT id, target, status FROM executions ORDER BY created_at DESC LIMIT 20;'
   ```
5. **Generate reports**
   ```bash
   python scripts/generate_report.py --format markdown --output data/reports/markdown/campaign.md
   ```
6. **Archive and reset**
   ```bash
   python scripts/backup_results.py --destination /mnt/backups/hyfuzz
   ```

## Running Specific Campaign Types

### Protocol-Specific Smoke Tests

```bash
python scripts/run_coap_test.py --config config/example_configs/config_coap.yaml
python scripts/run_modbus_test.py --config config/example_configs/config_modbus.yaml
python scripts/run_mqtt_test.py --config config/example_configs/config_mqtt.yaml
python scripts/run_http_test.py --config config/example_configs/config_safe.yaml
```

### Distributed Campaigns

1. Ensure the server has scheduled tasks for the client pool.
2. Start local workers with increased concurrency:
   ```bash
   python scripts/run_campaign.py --config config/example_configs/config_distributed.yaml --workers 8
   ```
3. Use `scripts/start_workers.py` and `scripts/stop_workers.py` if running under a process supervisor.

### Aggressive vs. Safe Profiles

- **Aggressive** (`config/example_configs/config_aggressive.yaml`)
  - Enables extended mutators and higher concurrency.
  - Use when running inside isolated lab environments.
- **Safe** (`config/example_configs/config_safe.yaml`)
  - Restricts payload size and disables high-risk mutations.
  - Recommended for production-adjacent or customer-facing environments.

## Instrumentation Controls

- Enable/disable tracers using `instrumentation_config.yaml`.
- Temporarily disable heavy instrumentation for stability testing:
  ```bash
  HYFUZZ_DISABLE_INSTRUMENTATION=1 python scripts/run_campaign.py --config ...
  ```
- Export coverage artefacts to LCOV:
  ```bash
  python scripts/instrumentation/export_coverage.py --output data/results/coverage/latest.info
  ```

## Crash Analysis Workflow

1. Inspect new crashes:
   ```bash
   python scripts/analyze_crashes.py --since "24h"
   ```
2. Reproduce a crash in isolation:
   ```bash
   python scripts/run_campaign.py --config config/example_configs/config_dev.yaml --replay CRASH_ID
   ```
3. Generate a crash report bundle:
   ```bash
   python scripts/generate_report.py --format crash --crash-id CRASH_ID
   ```
4. Forward to the HyFuzz server if needed:
   ```bash
   python scripts/analyze_crashes.py --export --destination /tmp/crash_bundle.zip
   ```

## Monitoring & Alerting

- Metrics collection:
  ```bash
  python scripts/monitor_client.py --push --interval 30
  ```
- Configure notifiers by editing `notification_config.yaml` and running:
  ```bash
  python scripts/monitor_client.py --alert-on degraded
  ```
- Logs rotate automatically; use `scripts/maintenance/rotate_logs.sh` for manual rotation.

## Maintenance Tasks

| Task | Command |
|------|---------|
| Clean temp files | `scripts/maintenance/cleanup_old_results.sh` |
| Vacuum SQLite DB | `scripts/maintenance/optimize_database.sh` |
| Update dependencies | `scripts/maintenance/update_client.sh` |
| Backup database | `scripts/backup_results.py --database-only` |

## Troubleshooting Checklist

1. **Connection issues** – Verify `scripts/test_connection.py`, review firewall, confirm MCP endpoint.
2. **Sandbox failures** – Check `logs/sandbox.log`, ensure kernel supports namespaces/cgroups.
3. **Instrumentation errors** – Validate tracer binaries exist; disable instrumentation temporarily to
   isolate the issue.
4. **Missing results** – Ensure `data/database/client.db` is writable and disk space is sufficient.
5. **High load** – Tune worker counts in `execution_config.yaml`, reduce instrumentation sampling rate.

For a comprehensive troubleshooting reference, read [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
