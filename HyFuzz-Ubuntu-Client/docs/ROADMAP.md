# Roadmap

The roadmap outlines planned enhancements for upcoming HyFuzz client releases. Timelines are indicative
and may shift based on community feedback and research outcomes.

## Near-Term (Q2)

- [ ] Finalise gRPC handler with streaming call support and bidirectional fuzzing.
- [ ] Integrate kernel-level eBPF tracing for lightweight syscall capture.
- [ ] Expand distributed scheduler with backpressure signalling from server.
- [ ] Publish reference Grafana dashboards for monitoring metrics.
- [ ] Add automated crash replay pipeline in CI using GitHub Actions runners.

## Mid-Term (Q3)

- [ ] Support hardware-assisted coverage using Intel Processor Trace.
- [ ] Implement remote object storage backend for artefacts (S3, MinIO).
- [ ] Introduce user-defined protocol templates via configuration-only extensions.
- [ ] Enhance notification subsystem with Microsoft Teams and PagerDuty integrations.
- [ ] Provide Terraform modules for provisioning client pools in major cloud providers.

## Long-Term (Q4+)

- [ ] Hybrid fuzzing mode combining symbolic execution hints from the server.
- [ ] ML-driven prioritisation of targets based on historical exploit success.
- [ ] Web-based operator console with live campaign control (FastAPI + Vue/React).
- [ ] Automatic remediation suggestions leveraging server-side LLM chains of thought.

## Completed in Phase 3

- ✅ Expanded protocol support (MQTT, HTTP, gRPC).
- ✅ Instrumentation suite with coverage, ptrace, and sanitizer ingestion.
- ✅ Crash analysis pipeline with exploitability scoring and deduplication.
- ✅ Reporting subsystem for HTML/JSON/Markdown/CSV outputs.
- ✅ Monitoring and alerting for distributed client fleets.

Contributions are welcome. Proposals should be discussed via issues before implementation to ensure
alignment with platform direction.
