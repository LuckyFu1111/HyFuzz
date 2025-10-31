# Troubleshooting Guide

Use this guide to diagnose common issues encountered when running the HyFuzz Ubuntu client.

## Connectivity Problems

| Symptom | Checks |
|---------|--------|
| Cannot reach server | Verify `MCP_ENDPOINT` in `.env`, run `scripts/test_connection.py`, inspect firewall/NAT rules |
| Frequent disconnects | Check `logs/mcp_client.log` for retries, adjust heartbeat interval in `config/execution_config.yaml` |
| Authentication failures | Ensure API keys/tokens are present in `.env` and valid on the server |

## Execution Failures

- **Sandbox initialisation errors**
  - Confirm namespaces and cgroups are supported: `lsns`, `lscgroup`.
  - Review `logs/sandbox.log` for missing binaries or permission issues.
  - Re-run `scripts/configure_sandbox.sh` to repair profiles.
- **Timeouts**
  - Increase `execution.timeout_seconds` in `execution_config.yaml`.
  - Reduce instrumentation overhead or worker counts.
- **High resource usage**
  - Enable resource throttling in `sandbox_config.yaml`.
  - Use `scripts/monitor_client.py` to observe CPU/memory trends.

## Instrumentation Issues

- **Coverage data missing**
  - Ensure targets are compiled with coverage flags.
  - Confirm `coverage.enabled: true` in `instrumentation_config.yaml`.
  - Inspect `logs/instrumentation.log` for backend errors.
- **ptrace denied**
  - Disable Yama ptrace restrictions: `sudo sysctl kernel.yama.ptrace_scope=0`.
  - Run the client under the same user as the target process.

## Crash Analysis Gaps

- **No crashes recorded**
  - Check instrumentation is active and `signal_interceptor.py` is enabled.
  - Verify `data/results/crashes/` is writable.
- **Duplicate crashes**
  - Tune deduplication thresholds in `analysis_config.yaml`.
  - Run `python scripts/analyze_crashes.py --dedupe` to reprocess existing data.

## Reporting & Monitoring

- **Report generation fails**
  - Inspect `logs/reporting.log` for template errors.
  - Validate the SQLite database integrity: `python scripts/maintenance/optimize_database.sh`.
- **No alerts sent**
  - Confirm notifiers are enabled in `notification_config.yaml`.
  - Check external service credentials (Slack webhook, SMTP server).

## Recovery Steps

1. Restart the client:
   ```bash
   systemctl restart hyfuzz-client.service
   # or
   pkill -f start_client.py
   python scripts/start_client.py --config config/example_configs/config_dev.yaml
   ```
2. Clear temporary state if corrupted:
   ```bash
   rm -rf data/results/tmp/*
   ```
3. Restore from backup if necessary:
   ```bash
   python scripts/restore_results.py --source /mnt/backups/hyfuzz
   ```

## When to Escalate

- Repeated crashes in the client itself (not the target) – collect logs and open an issue.
- Persistent protocol negotiation failures – capture MCP traces and contact the server team.
- Suspected security incidents – follow organisational incident response procedures immediately.

Keep this guide alongside operational runbooks and update it as new edge cases are discovered.
