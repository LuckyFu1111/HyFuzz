# HyFuzz Documentation Index

Welcome to the HyFuzz documentation! This page serves as your central hub for navigating all documentation resources across the project.

## 📚 Documentation Structure

HyFuzz documentation is organized into three levels:

1. **Project-Level** (this directory) - Overview and getting started
2. **Component-Level** (component directories) - Component-specific guides
3. **Technical** (docs/ folders) - Detailed technical documentation

## 🚀 Getting Started

### New Users Start Here

1. **[README.md](README.md)** - Project overview and introduction
2. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
3. Choose your component documentation below

### Quick Links

- ⚡ [5-Minute Quick Start](QUICKSTART.md)
- 📖 [Main README](README.md)
- 🏗️ [Architecture Overview](HyFuzz-Windows-Server/docs/ARCHITECTURE.md)
- 🔌 [API Reference](HyFuzz-Windows-Server/docs/API.md)
- 🐛 [Troubleshooting](HyFuzz-Windows-Server/docs/TROUBLESHOOTING.md)

## 📦 Component Documentation

### Windows Server (Control Plane)

The Windows Server is the LLM-powered orchestration platform.

**Essential Reading:**
- [Windows Server README](HyFuzz-Windows-Server/README.md) - Component overview
- [Installation Guide](HyFuzz-Windows-Server/INSTALLATION.md) - Detailed installation
- [Setup Guide](HyFuzz-Windows-Server/SETUP_GUIDE.md) - Configuration and setup

**Technical Documentation** (`HyFuzz-Windows-Server/docs/`):

| Category | Document | Description |
|----------|----------|-------------|
| **Architecture** | [ARCHITECTURE.md](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) | System design and component overview |
| **API** | [API.md](HyFuzz-Windows-Server/docs/API.md) | REST API reference |
| **LLM** | [LLM_INTEGRATION.md](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md) | LLM configuration and usage |
| **Defense** | [DEFENSE_INTEGRATION.md](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md) | WAF/IDS integration |
| **Protocols** | [PROTOCOL_GUIDE.md](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md) | Supported protocols |
| **Monitoring** | [MONITORING_GUIDE.md](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md) | Metrics and dashboards |
| **Reports** | [REPORTING_GUIDE.md](HyFuzz-Windows-Server/docs/REPORTING.md) | Report generation |
| **Deployment** | [DEPLOYMENT.md](HyFuzz-Windows-Server/docs/DEPLOYMENT.md) | Production deployment |
| **Troubleshooting** | [TROUBLESHOOTING.md](HyFuzz-Windows-Server/docs/TROUBLESHOOTING.md) | Common issues |
| **FAQ** | [FAQ.md](HyFuzz-Windows-Server/docs/FAQ.md) | Frequently asked questions |

### macOS Server (Control Plane)

The macOS Server provides the same functionality as Windows Server with Apple Silicon optimizations.

**Essential Reading:**
- [macOS Server README](HyFuzz-Mac-Server/README.md) - Component overview
- [Installation Guide](HyFuzz-Mac-Server/INSTALLATION.md) - Detailed installation
- [Setup Guide](HyFuzz-Mac-Server/SETUP_GUIDE.md) - Configuration and setup
- [Performance Guide](HyFuzz-Mac-Server/docs/MACOS_PERFORMANCE.md) - Apple Silicon optimization

**Technical Documentation** (`HyFuzz-Mac-Server/docs/`):

Same structure as Windows Server, plus:
- [MACOS_PERFORMANCE.md](HyFuzz-Mac-Server/docs/MACOS_PERFORMANCE.md) - Performance optimization for Apple Silicon
- [METAL_ACCELERATION.md](HyFuzz-Mac-Server/docs/METAL_ACCELERATION.md) - Using Metal for LLM inference

### Ubuntu Client (Execution Engine)

The Ubuntu Client executes payloads and reports results back to the server.

**Essential Reading:**
- [Ubuntu Client README](HyFuzz-Ubuntu-Client/README.md) - Component overview
- [Setup Guide](HyFuzz-Ubuntu-Client/SETUP_GUIDE.md) - Configuration and setup

**Technical Documentation** (`HyFuzz-Ubuntu-Client/docs/`):

| Category | Document | Description |
|----------|----------|-------------|
| **Architecture** | [ARCHITECTURE.md](HyFuzz-Ubuntu-Client/docs/ARCHITECTURE.md) | Client design overview |
| **Usage** | [USAGE.md](HyFuzz-Ubuntu-Client/docs/USAGE.md) | Daily operations guide |
| **Instrumentation** | [INSTRUMENTATION.md](HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md) | Tracing and monitoring |
| **Fuzzing** | [FUZZING.md](HyFuzz-Ubuntu-Client/docs/FUZZING.md) | Fuzzing configuration |
| **Protocols** | [PROTOCOLS.md](HyFuzz-Ubuntu-Client/docs/PROTOCOLS.md) | Protocol handlers |
| **Crash Analysis** | [CRASH_ANALYSIS.md](HyFuzz-Ubuntu-Client/docs/CRASH_ANALYSIS.md) | Crash triage guide |
| **Sandbox** | [SANDBOX_GUIDE.md](HyFuzz-Ubuntu-Client/docs/SANDBOX_GUIDE.md) | Sandbox configuration |
| **Deployment** | [DEPLOYMENT.md](HyFuzz-Ubuntu-Client/docs/DEPLOYMENT.md) | Installation guide |

## 🎯 Documentation by Topic

### Installation & Setup

1. [Quick Start Guide](QUICKSTART.md) - Get running in 5 minutes
2. [Windows Server Installation](HyFuzz-Windows-Server/INSTALLATION.md)
3. [macOS Server Installation](HyFuzz-Mac-Server/INSTALLATION.md)
4. [Ubuntu Client Setup](HyFuzz-Ubuntu-Client/SETUP_GUIDE.md)

### Architecture & Design

1. [System Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) - Overall design
2. [Server Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) - Server components
3. [Client Architecture](HyFuzz-Ubuntu-Client/docs/ARCHITECTURE.md) - Client components
4. [MCP Protocol](HyFuzz-Windows-Server/docs/MCP_PROTOCOL.md) - Communication protocol

### Usage & Operations

1. [Campaign Management](HyFuzz-Windows-Server/docs/CAMPAIGNS.md) - Creating and managing campaigns
2. [API Usage](HyFuzz-Windows-Server/docs/API.md) - REST API guide
3. [Web Dashboard](HyFuzz-Windows-Server/docs/DASHBOARD.md) - Dashboard usage
4. [Result Analysis](HyFuzz-Windows-Server/docs/ANALYSIS.md) - Analyzing results

### LLM Integration

1. [LLM Integration Guide](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md) - Overview
2. [Ollama Setup](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md#ollama) - Local LLM
3. [OpenAI Integration](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md#openai) - Cloud LLM
4. [Prompt Engineering](HyFuzz-Windows-Server/docs/PROMPT_ENGINEERING.md) - Optimizing prompts

### Protocol Support

1. [Protocol Guide](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md) - Overview
2. [CoAP Fuzzing](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md#coap) - IoT protocol
3. [Modbus Fuzzing](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md#modbus) - Industrial protocol
4. [MQTT Fuzzing](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md#mqtt) - IoT messaging
5. [HTTP/HTTPS Fuzzing](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md#http) - Web protocols

### Defense Integration

1. [Defense Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md) - Overview
2. [WAF Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md#waf) - Web application firewall
3. [IDS Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md#ids) - Intrusion detection

### Monitoring & Observability

1. [Monitoring Guide](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md) - Overview
2. [Metrics](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md#metrics) - Available metrics
3. [Grafana Dashboards](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md#grafana) - Visualization
4. [Alerting](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md#alerts) - Setting up alerts

### Deployment

1. [Deployment Guide](HyFuzz-Windows-Server/docs/DEPLOYMENT.md) - Overview
2. [Docker Deployment](HyFuzz-Windows-Server/docs/DEPLOYMENT.md#docker) - Containerized deployment
3. [Production Best Practices](HyFuzz-Windows-Server/docs/DEPLOYMENT.md#production) - Security and scale
4. [Distributed Setup](HyFuzz-Windows-Server/docs/DISTRIBUTED_FUZZING.md) - Multi-client deployment

### Development

1. [Contributing Guide](CONTRIBUTING.md) - How to contribute
2. [Development Workflow](HyFuzz-Windows-Server/docs/DEVELOPMENT.md) - Developer guide
3. [Testing Guide](HyFuzz-Windows-Server/docs/TESTING.md) - Writing and running tests
4. [Code Style](CONTRIBUTING.md#coding-standards) - Coding standards

### Troubleshooting

1. [Quick Start Troubleshooting](QUICKSTART.md#-common-issues--solutions) - Common quick start issues
2. [Server Troubleshooting](HyFuzz-Windows-Server/docs/TROUBLESHOOTING.md) - Server issues
3. [Client Troubleshooting](HyFuzz-Ubuntu-Client/docs/TROUBLESHOOTING.md) - Client issues
4. [FAQ](HyFuzz-Windows-Server/docs/FAQ.md) - Frequently asked questions

## 🔬 Research & Academic

### Thesis Results

The `thesis_results/` directory contains comprehensive validation and comparison data:

- **Baseline Comparisons**: Results comparing HyFuzz against AFL, AFL++, AFLNet, and libFuzzer
- **Protocol Testing**: Extensive testing of CoAP and Modbus implementations
- **Statistical Analysis**: Publication-quality analysis and plots
- **Methodology**: Research methodology and experimental setup

Documentation:
- [Thesis Results README](thesis_results/README.md)
- [Testing Methodology](thesis_results/docs/METHODOLOGY.md)
- [Results Analysis](thesis_results/docs/ANALYSIS.md)

### Academic Citations

If you use HyFuzz in your research, see [AUTHORS.md](AUTHORS.md#academic-citations) for citation information.

## 📋 Governance & Community

### Project Governance

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community standards
- [Security Policy](SECURITY.md) - Security reporting
- [License](LICENSE) - Apache License 2.0
- [Authors](AUTHORS.md) - Contributors and acknowledgments

### Community Resources

- [GitHub Issues](https://github.com/LuckyFu1111/HyFuzz/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions) - Questions and community support
- [Changelog](CHANGELOG.md) - Version history

## 🗺️ Documentation Roadmap

### Planned Documentation

Future documentation planned for upcoming releases:

- **Video Tutorials**: Step-by-step video guides
- **Use Case Studies**: Real-world fuzzing examples
- **Plugin Development**: Creating custom plugins
- **Advanced Topics**: Deep dives into specific features
- **Translations**: Non-English documentation

### Contributing to Documentation

We welcome documentation improvements! See [CONTRIBUTING.md](CONTRIBUTING.md#documentation) for guidelines.

## 📖 Reading Paths

### Path 1: Quick Setup (30 minutes)

For users who want to get started quickly:

1. [README.md](README.md) - 5 minutes
2. [QUICKSTART.md](QUICKSTART.md) - 10 minutes
3. Run first campaign - 15 minutes

### Path 2: Understanding HyFuzz (2 hours)

For users who want to understand the system:

1. [README.md](README.md) - 10 minutes
2. [Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) - 30 minutes
3. [LLM Integration](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md) - 20 minutes
4. [Protocol Guide](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md) - 30 minutes
5. [API Reference](HyFuzz-Windows-Server/docs/API.md) - 30 minutes

### Path 3: Production Deployment (4 hours)

For users deploying to production:

1. [README.md](README.md) - 10 minutes
2. [Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) - 30 minutes
3. [Installation Guides](HyFuzz-Windows-Server/INSTALLATION.md) - 45 minutes
4. [Deployment Guide](HyFuzz-Windows-Server/docs/DEPLOYMENT.md) - 60 minutes
5. [Monitoring Setup](HyFuzz-Windows-Server/docs/MONITORING_GUIDE.md) - 45 minutes
6. [Security Best Practices](SECURITY.md) - 30 minutes

### Path 4: Contributing (3 hours)

For developers who want to contribute:

1. [Contributing Guide](CONTRIBUTING.md) - 30 minutes
2. [Development Workflow](HyFuzz-Windows-Server/docs/DEVELOPMENT.md) - 45 minutes
3. [Testing Guide](HyFuzz-Windows-Server/docs/TESTING.md) - 45 minutes
4. [Code Style](CONTRIBUTING.md#coding-standards) - 30 minutes
5. [Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md) - 30 minutes

## 🔍 Finding What You Need

### Search Tips

1. **By Component**: Navigate to component directories first
2. **By Topic**: Use the "Documentation by Topic" section above
3. **By Task**: Use the "Reading Paths" section
4. **By Problem**: Check troubleshooting sections first

### Still Can't Find It?

- Check the [FAQ](HyFuzz-Windows-Server/docs/FAQ.md)
- Search [GitHub Issues](https://github.com/LuckyFu1111/HyFuzz/issues)
- Ask in [GitHub Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions)

## 📝 Documentation Feedback

Found a documentation issue? Please:

1. [Open an issue](https://github.com/LuckyFu1111/HyFuzz/issues/new) with the label `documentation`
2. Submit a PR with improvements
3. Discuss in [GitHub Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions)

---

**Last Updated**: January 2025

Happy Fuzzing! 🚀
