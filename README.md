# HyFuzz - Intelligent Distributed Fuzzing Platform

<div align="center">

**LLM-Driven • Defense-Aware • Protocol-Agnostic • Cross-Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

</div>

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see each component's documentation for contribution guidelines.

---

## 📧 Support

- **Documentation**: Check component-specific README files
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions

---

## 🎖️ Project Status

- ✅ **Windows Server**: Production ready
- ✅ **macOS Server**: Production ready (with Apple Silicon optimization)
- ✅ **Ubuntu Client**: Production ready

---

**Version**: 2.0.0  
**Last Updated**: 2025-01-XX  
**Maintainers**: HyFuzz Development Team
