# Frequently Asked Questions

## General

**Q: Which operating systems are supported?**  
A: Ubuntu 22.04 LTS and later. Other Debian-based distributions may work but are not officially
validated.

**Q: Can I run the client alongside other fuzzers?**  
A: Yes. Use the scheduling subsystem to allocate workloads and ensure CPU/memory isolation via cgroups.

**Q: How do I upgrade to a new release?**  
A: Pull the latest code, reinstall dependencies if required, run migrations, and restart services. See
[DEPLOYMENT.md](DEPLOYMENT.md#updating-clients).

## Configuration

**Q: Where do I configure server endpoints and authentication?**  
A: In `.env` (MCP endpoint, credentials) and `config/execution_config.yaml` (transport defaults).

**Q: How can I disable specific protocols?**  
A: Set `enabled: false` in `config/protocol_config.yaml` for each protocol.

**Q: How do I tune sandbox limits?**  
A: Edit `config/sandbox_config.yaml` (CPU shares, memory limits, namespace options) or choose a different
sandbox profile in `execution_config.yaml`.

## Operations

**Q: Campaigns are slow. What should I check?**  
A: Review CPU/memory utilisation, reduce instrumentation intensity, or increase worker count. Performance
tests under `tests/performance/` help quantify changes.

**Q: How do I monitor multiple clients?**  
A: Enable Prometheus exporters (`--export prometheus`) and aggregate dashboards via Grafana or the server
monitoring module.

**Q: Where are logs stored?**  
A: In the `logs/` directory; each subsystem has its own log file (e.g., `execution.log`,
`instrumentation.log`, `crash.log`).

## Troubleshooting

**Q: The client cannot reach the server.**  
A: Validate network connectivity, firewall rules, and MCP endpoint values. Use
`scripts/test_connection.py` to confirm.

**Q: Crashes are not appearing in reports.**  
A: Ensure instrumentation is enabled, check `logs/crash.log` for errors, and run
`python scripts/analyze_crashes.py --list` to confirm crash ingestion.

**Q: Coverage metrics are zero.**  
A: Verify coverage instrumentation is enabled (`config/instrumentation_config.yaml`) and that targets are
built with coverage flags.

## Development

**Q: How can I add a new protocol handler?**  
A: Follow the steps in [PROTOCOLS.md](PROTOCOLS.md#adding-a-new-protocol) and update tests/documentation
accordingly.

**Q: Where are example datasets for testing?**  
A: Under `data/payloads/`, `data/targets/`, and `tests/fixtures/`.

**Q: How do I contribute changes?**  
A: Review [`CONTRIBUTING.md`](../CONTRIBUTING.md) and open a pull request with tests and documentation
updates.

If your question is not covered here, please open an issue on the repository or contact the maintainer
team directly.
