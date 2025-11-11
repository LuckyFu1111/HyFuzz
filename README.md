# HyFuzz - Intelligent Distributed Fuzzing Platform

<div align="center">

**LLM-Driven • Defense-Aware • Protocol-Agnostic • Cross-Platform**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)]()

</div>

---

## 📖 About HyFuzz

**HyFuzz** is an intelligent distributed fuzzing platform that combines the power of Large Language Models (LLMs) with traditional fuzzing techniques to discover security vulnerabilities in network protocols and IoT/industrial systems.

### What Makes HyFuzz Unique?

- **🤖 AI-Powered Intelligence**: Leverages LLM-based Chain-of-Thought reasoning to generate contextually relevant payloads, moving beyond random mutation strategies
- **🛡️ Defense-Aware Testing**: Integrates with WAF/IDS systems to understand defensive mechanisms and generate evasion-aware payloads
- **🌐 Protocol-Agnostic**: Supports multiple protocol families including CoAP, Modbus, MQTT, HTTP, gRPC, and JSON-RPC
- **📊 Distributed Architecture**: Scales across multiple execution clients for parallel testing campaigns
- **🔄 Adaptive Learning**: Continuously learns from execution results to refine fuzzing strategies

### Use Cases

- **IoT Security Testing**: Discover vulnerabilities in CoAP and MQTT-based IoT devices
- **Industrial Control Systems**: Test Modbus implementations in critical infrastructure
- **Web Application Security**: AI-driven fuzzing of HTTP/HTTPS APIs and endpoints
- **Protocol Implementation Testing**: Validate RFC compliance and discover edge cases
- **Security Research**: Academic and professional security research with comprehensive instrumentation

### Research Background

HyFuzz was developed as part of academic research into intelligent fuzzing methodologies. The platform includes a comprehensive validation suite (`thesis_results/`) with comparisons against baseline fuzzers (AFL, AFL++, AFLNet, libFuzzer) and publication-quality analysis tools.

---

## 📁 Project Structure

HyFuzz is a distributed fuzzing platform consisting of three main components:

```
HyFuzz/
├── HyFuzz-Windows-Server/    # Windows control plane (LLM + orchestration)
├── HyFuzz-Mac-Server/         # macOS control plane (optimized for Apple Silicon)
├── HyFuzz-Ubuntu-Client/      # Linux execution engine (payload execution)
└── README.md                  # This file
```

---

## 🎯 Quick Navigation

### Server Components (Control Plane)

#### **Windows Server**
```bash
cd HyFuzz-Windows-Server
```
📖 [Windows Server Documentation](HyFuzz-Windows-Server/README.md)

**Features:**
- LLM-powered payload generation (Ollama/OpenAI)
- Defense system integration
- Web dashboard and monitoring
- Campaign orchestration
- Windows 10/11 optimized

**Quick Start:**
```bash
cd HyFuzz-Windows-Server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/start_server.py
```

---

#### **macOS Server**
```bash
cd HyFuzz-Mac-Server
```
📖 [macOS Server Documentation](HyFuzz-Mac-Server/README.md)

**Features:**
- Same functionality as Windows Server
- Apple Silicon (M1/M2/M3/M4) optimization
- Metal Performance Shaders acceleration
- Unified memory architecture support
- LaunchD service integration

**Quick Start:**
```bash
cd HyFuzz-Mac-Server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run automatic optimization
python3 scripts/optimize_macos.py

# Start server
./scripts/start_server.sh
```

📖 [macOS Performance Guide](HyFuzz-Mac-Server/docs/MACOS_PERFORMANCE.md)

---

### Client Component (Execution Engine)

#### **Ubuntu Client**
```bash
cd HyFuzz-Ubuntu-Client
```
📖 [Ubuntu Client Documentation](HyFuzz-Ubuntu-Client/README.md)

**Features:**
- Payload execution and sandboxing
- Instrumentation (strace, perf, ltrace)
- Protocol handlers (CoAP, Modbus, MQTT, HTTP)
- Crash detection and analysis
- Result reporting

**Quick Start:**
```bash
cd HyFuzz-Ubuntu-Client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/start_client.py
```

---

## 🚀 Getting Started

### Prerequisites

- **Server**: Windows 10/11, macOS 12+, or Linux with Python 3.9+
- **Client**: Ubuntu 22.04+ with Python 3.9+
- **LLM Service**: Ollama (local) or OpenAI API key
- **Memory**: 8GB minimum, 16GB+ recommended

### Complete Setup

1. **Choose and set up a server** (Windows or macOS):
   ```bash
   # For Windows
   cd HyFuzz-Windows-Server
   # Follow Windows Server README

   # OR for macOS
   cd HyFuzz-Mac-Server
   # Follow macOS Server README
   ```

2. **Set up the client** (Ubuntu):
   ```bash
   cd HyFuzz-Ubuntu-Client
   # Follow Ubuntu Client README
   ```

3. **Run your first campaign**:
   - Configure server and client connection
   - Start server, then client
   - Launch a fuzzing campaign via dashboard or API

---

## 📖 Documentation

Each component has its own comprehensive documentation:

### Windows Server
- [README](HyFuzz-Windows-Server/README.md) - Overview and setup
- [INSTALLATION](HyFuzz-Windows-Server/INSTALLATION.md) - Detailed installation
- [SETUP_GUIDE](HyFuzz-Windows-Server/SETUP_GUIDE.md) - Configuration guide
- [docs/](HyFuzz-Windows-Server/docs/) - Complete documentation

### macOS Server
- [README](HyFuzz-Mac-Server/README.md) - Overview and setup
- [INSTALLATION](HyFuzz-Mac-Server/INSTALLATION.md) - Detailed installation
- [MACOS_PERFORMANCE](HyFuzz-Mac-Server/docs/MACOS_PERFORMANCE.md) - Performance optimization
- [docs/](HyFuzz-Mac-Server/docs/) - Complete documentation

### Ubuntu Client
- [README](HyFuzz-Ubuntu-Client/README.md) - Overview and setup
- [SETUP_GUIDE](HyFuzz-Ubuntu-Client/SETUP_GUIDE.md) - Configuration guide
- [docs/](HyFuzz-Ubuntu-Client/docs/) - Complete documentation

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          Server (Windows or macOS)                   │
│  ┌─────────────────────────────────────────────┐   │
│  │  • LLM Payload Generator (Ollama/OpenAI)    │   │
│  │  • Defense System Integrator                │   │
│  │  • Campaign Management                      │   │
│  │  • Web Dashboard                            │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ Network (MCP Protocol)
                     ▼
┌─────────────────────────────────────────────────────┐
│              Ubuntu Client                           │
│  ┌─────────────────────────────────────────────┐   │
│  │  • Payload Execution Engine                 │   │
│  │  • Instrumentation (strace, perf, gdb)     │   │
│  │  • Protocol Handlers                        │   │
│  │  • Crash Detection                          │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **🤖 LLM-Driven Intelligence**: AI-powered payload generation and quality assessment
- **🛡️ Defense Integration**: Real-time defense system analysis and risk scoring
- **🌐 Multi-Protocol**: CoAP, Modbus, MQTT, HTTP, gRPC, JSON-RPC support
- **📊 Comprehensive Monitoring**: Real-time dashboards and metrics
- **🚀 Distributed Execution**: Scalable across multiple clients
- **🔄 Feedback Loops**: Continuous learning from results
- **💻 Cross-Platform**: Windows Server, macOS Server, Linux Client

---

## 🔧 Development

Each component is self-contained with its own:
- Source code (`src/`)
- Tests (`tests/`)
- Scripts (`scripts/`)
- Configuration (`config/`)
- Documentation (`docs/`)

This allows independent development and deployment of each component.

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 HyFuzz Development Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or reporting issues, your help is appreciated.

### How to Contribute

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards in each component
3. **Write or update tests** for your changes
4. **Ensure all tests pass** by running the test suite
5. **Submit a pull request** with a clear description of your changes

### Contribution Areas

- 🐛 Bug fixes and error handling improvements
- ✨ New protocol support or feature additions
- 📚 Documentation improvements and translations
- 🧪 Test coverage expansion
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations

For detailed contribution guidelines, see:
- [Windows Server Contributing Guide](HyFuzz-Windows-Server/CONTRIBUTING.md)
- [macOS Server Contributing Guide](HyFuzz-Mac-Server/CONTRIBUTING.md)
- [Ubuntu Client Contributing Guide](HyFuzz-Ubuntu-Client/CONTRIBUTING.md)

### Code of Conduct

Please note that this project adheres to a Code of Conduct. By participating, you are expected to uphold this code. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

---

## 📧 Support

### Getting Help

- **📖 Documentation**: Check component-specific README files and the `/docs` folder in each component
- **🐛 Bug Reports**: [Create an issue](https://github.com/LuckyFu1111/HyFuzz/issues/new) with detailed reproduction steps
- **💬 Discussions**: [Join GitHub Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions) for questions and community support
- **🔒 Security Issues**: See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities

### Quick Links

- [5-Minute Quick Start](QUICKSTART.md)
- [Architecture Documentation](HyFuzz-Windows-Server/docs/ARCHITECTURE.md)
- [API Reference](HyFuzz-Windows-Server/docs/API.md)
- [Troubleshooting Guides](HyFuzz-Windows-Server/docs/TROUBLESHOOTING.md)
- [FAQ](HyFuzz-Windows-Server/docs/FAQ.md)

---

## 🎖️ Project Status

- ✅ **Windows Server**: Production ready
- ✅ **macOS Server**: Production ready (with Apple Silicon optimization)
- ✅ **Ubuntu Client**: Production ready

---

<div align="center">

**Version**: 2.0.0
**Last Updated**: January 2025
**Maintainers**: HyFuzz Development Team

[Documentation](https://github.com/LuckyFu1111/HyFuzz) • [Issues](https://github.com/LuckyFu1111/HyFuzz/issues) • [Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions)

</div>
