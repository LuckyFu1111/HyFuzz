# Documentation Guide

The `docs/` directory contains deep dives for each Phase 3 subsystem of the HyFuzz Ubuntu client. The
recommended reading order and relationships are outlined below.

## Quick Navigation

| Area | Purpose | Start Here |
|------|---------|-----------|
| Getting started | Install, configure, and validate the client | [SETUP.md](SETUP.md) |
| Daily operations | Launch campaigns and manage results | [USAGE.md](USAGE.md) |
| Architecture | Understand subsystem responsibilities and data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Instrumentation | Configure tracing, coverage, and sanitizers | [INSTRUMENTATION.md](INSTRUMENTATION.md) |
| Fuzzing & Protocols | Tune fuzzers and enable additional protocols | [FUZZING.md](FUZZING.md), [PROTOCOLS.md](PROTOCOLS.md) |
| Crash triage | Investigate failures and deduplicate issues | [CRASH_ANALYSIS.md](CRASH_ANALYSIS.md) |
| Monitoring & Reporting | Track fleet health and export artefacts | [MONITORING.md](MONITORING.md), [REPORTING_GUIDE.md](REPORTING_GUIDE.md) |
| Target management | Discover and maintain campaign inventories | [TARGET_MANAGEMENT.md](TARGET_MANAGEMENT.md) |
| Deployment | Package the client for VirtualBox, Docker, or bare metal | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Reference | API surface, FAQs, roadmap, troubleshooting | [API.md](API.md), [FAQ.md](FAQ.md), [ROADMAP.md](ROADMAP.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

## Audience Map

- **Operators** – Focus on setup, usage, monitoring, and troubleshooting.
- **Protocol engineers** – Review protocols, fuzzing, instrumentation, and notebooks.
- **Security analysts** – Use crash analysis, reporting, and target management guides.
- **Contributors** – Combine this documentation with repository-level `CONTRIBUTING.md` and
  `CODE_OF_CONDUCT.md`.

## Conventions

- Commands are written for Ubuntu 22.04+. Prefix with `sudo` when required.
- File paths are relative to the repository root unless otherwise noted.
- Configuration examples use YAML fragments and environment variables stored in `.env`.
- Symbols:
  - ✅ indicates tasks validated during Phase 3 acceptance.
  - ⚙️ denotes configuration knobs that may require tuning per deployment.
  - 🧪 highlights instrumentation or analysis steps that can generate heavy load.

## Related Resources

- [`notebooks/`](../notebooks/) – exploratory data analysis, coverage visualisation, campaign reporting.
- [`scripts/`](../scripts/) – operational helpers referenced throughout the guides.
- [`tests/`](../tests/) – canonical examples of using protocol handlers, instrumentation, and analyzers.

For missing topics or improvement ideas, open an issue or submit a pull request so the documentation
stays aligned with the evolving architecture.
