# Crash Analysis Guide

The analysis subsystem triages crashes generated during fuzzing campaigns, determines severity, and
produces artefacts for developers and security analysts.

## Pipeline Overview

1. **Signal capture** – Instrumentation intercepts fatal signals and stores metadata in
   `data/results/crashes/`.
2. **Crash ingestion** – `src/analysis/crash_analyzer.py` correlates signals with execution context and
   sandbox logs.
3. **Artefact collection** – Core dumps, sanitizer logs, and coverage snapshots are linked to the crash
   record.
4. **Exploitability scoring** – `exploitability_checker.py` ranks crashes (High/Medium/Low/Informational).
5. **Deduplication** – `deduplicator.py` clusters crashes based on stack traces, sanitizer fingerprints,
   and coverage deltas.
6. **Reporting** – `report_generator.py` compiles crash reports and attaches reproduction steps.

## Crash Artefacts

| Artefact | Location | Description |
|----------|----------|-------------|
| Crash JSON | `data/results/crashes/*.json` | Structured record with metadata, stack trace, exploitability |
| Core dump | `/tmp/core.*` (configurable) | Raw core file captured from sandboxed process |
| Sanitizer log | `logs/crash.log` / `logs/instrumentation.log` | ASAN/UBSAN/Valgrind output |
| Reproducer payload | `data/results/crashes/<id>/payload.bin` | Input that triggered the crash |
| Coverage snapshot | `data/results/coverage/<id>.info` | Coverage state at time of crash |

## Working with Crashes

- List recent crashes:
  ```bash
  python scripts/analyze_crashes.py --list --limit 10
  ```
- Show detailed crash information:
  ```bash
  python scripts/analyze_crashes.py --crash-id CRASH_UUID --verbose
  ```
- Export crash bundle for sharing:
  ```bash
  python scripts/analyze_crashes.py --crash-id CRASH_UUID --export --destination /tmp/crash_bundle.zip
  ```
- Generate a crash-focused report:
  ```bash
  python scripts/generate_report.py --format crash --crash-id CRASH_UUID
  ```

## Exploitability Levels

| Level | Description | Recommended Action |
|-------|-------------|-------------------|
| High | Clear memory corruption or remote code execution primitives | Immediate developer attention, coordinate with server team |
| Medium | Likely security impact but requires additional constraints | Schedule deep triage, collect more telemetry |
| Low | Low impact bug, limited abuse potential | Document for future reference, optional fix |
| Informational | Benign crash (e.g., expected assertion) | Ignore unless repeated |

## Integrating with Server Workflows

- The client uploads crash summaries to the server via MCP, enabling central dashboards and LLM-assisted
  judgement.
- Use `python scripts/analyze_crashes.py --sync` to force immediate synchronisation.

## Best Practices

- Keep core dumps manageable by rotating `/tmp` and compressing older dumps.
- Attach debugger reproductions when submitting to upstream engineering teams.
- Automate triage using CI by replaying high-severity crashes (`--replay` option).
- Monitor deduplication quality; adjust thresholds in `config/analysis_config.yaml` if too many/too few
  clusters are produced.

For visual analysis and clustering, explore `notebooks/06_crash_analysis.ipynb` and
`notebooks/09_campaign_reporting.ipynb`.
