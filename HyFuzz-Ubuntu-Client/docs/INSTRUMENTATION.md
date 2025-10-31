# Instrumentation Guide

The instrumentation subsystem captures execution telemetry to improve crash analysis, coverage reporting,
and adaptive fuzzing decisions.

## Components

| File | Responsibility |
|------|----------------|
| `instrumentor.py` | Orchestrates tracer lifecycle, manages plugins |
| `ptrace_handler.py` | Attaches ptrace to processes, records syscalls |
| `strace_parser.py` / `ltrace_parser.py` | Parses syscall/libcall logs into structured events |
| `coverage_tracker.py` | Aggregates coverage data, produces LCOV reports |
| `memory_tracker.py` | Collects allocator statistics and RSS snapshots |
| `syscall_monitor.py` | Detects suspicious syscall sequences |
| `signal_interceptor.py` | Captures crash signals and forwards metadata |
| `instrumentation_models.py` | Shared dataclasses for events |

## Configuration

Edit `config/instrumentation_config.yaml`:

```yaml
instrumentation:
  ptrace: true
  strace:
    enabled: true
    follow_forks: true
  coverage:
    enabled: true
    backend: lcov
  sanitizers:
    asan: true
    ubsan: false
  sampling:
    interval_ms: 100
```

Toggle instrumentation per campaign via environment variables:

```bash
HYFUZZ_DISABLE_INSTRUMENTATION=1 python scripts/run_campaign.py --config ...
HYFUZZ_ENABLE_COVERAGE=1 python scripts/run_campaign.py --config ...
```

## Coverage Workflow

1. Enable coverage in the configuration.
2. Run campaigns as normal; LCOV files are stored under `data/results/coverage/`.
3. Use `scripts/instrumentation/export_coverage.py` to merge runs:
   ```bash
   python scripts/instrumentation/export_coverage.py --output data/results/coverage/merged.info
   ```
4. Visualise coverage using `notebooks/07_coverage_visualization.ipynb` or external tools like `genhtml`.

## Crash Signal Handling

- `signal_interceptor.py` listens for `SIGSEGV`, `SIGABRT`, `SIGILL`, etc., and generates crash records.
- Crash metadata is forwarded to the analysis subsystem (`src/analysis/crash_analyzer.py`).
- Logs are written to `logs/instrumentation.log` for auditing.

## Sanitizer Integration

- Build targets with sanitizers enabled (`ASAN_OPTIONS`, `UBSAN_OPTIONS`, etc.).
- Instrumentation collects sanitizer output and attaches it to crash reports.
- Configure log paths in `config/sandbox_config.yaml` if sanitizer output is redirected.

## Performance Tips

- Disable tracing for protocols that already expose high-quality telemetry to reduce overhead.
- Adjust sampling interval for memory metrics to balance fidelity vs. resource usage.
- Offload coverage processing to background workers when running aggressive campaigns.

## Validation

Run the instrumentation unit tests to verify configuration changes:

```bash
pytest tests/unit/test_instrumentation.py
pytest tests/performance/test_instrumentation_perf.py
```

Refer to [`CRASH_ANALYSIS.md`](CRASH_ANALYSIS.md) to see how instrumentation output feeds into crash
triage, and [`MONITORING.md`](MONITORING.md) for runtime metric exports.
