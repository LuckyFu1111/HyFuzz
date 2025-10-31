# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-01-27
### Added
- Initial public release of the HyFuzz Ubuntu client for Phase 3.
- Introduced multi-protocol execution support with CoAP, Modbus, MQTT, HTTP, and gRPC handlers.
- Added instrumentation, analysis, reporting, monitoring, notifications, scheduling, and fuzzing subsystems.
- Integrated Ollama-based LLM payload generation hooks and IDS-inspired judgement pipeline.

### Changed
- Refined configuration layout to support campaign level tuning.

### Fixed
- Stabilised orchestration loop and storage integration when running multiple campaigns.

