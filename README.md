# HyFuzz - Intelligent Distributed Fuzzing Platform

<div align="center">

**LLM-Driven • Defense-Aware • Protocol-Agnostic • Distributed**

[Quick Start](#quick-start) •
[Documentation](#documentation) •
[Architecture](#architecture) •
[Contributing](#contributing) •
[Support](#support)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Support and Community](#support-and-community)
- [License](#license)

## Overview

**HyFuzz** is an intelligent distributed fuzzing platform that combines Large Language Model (LLM) driven payload generation with defense-aware analysis and cross-platform execution capabilities. The platform orchestrates sophisticated fuzzing campaigns across multiple protocols and targets, providing real-time defense system integration and automated quality assessment.

### What Makes HyFuzz Unique?

- **LLM-Driven Intelligence**: Leverages language models (Ollama, OpenAI, Azure OpenAI) for intelligent payload generation and quality assessment
- **Defense Integration**: Real-time defense system analysis with risk scoring and automated verdict generation
- **Protocol Agnostic**: Built-in support for CoAP, Modbus, MQTT, HTTP with extensible protocol framework
- **Distributed Architecture**: Windows-based control plane coordinating with Ubuntu execution agents
- **Feedback Loops**: Continuous learning from execution results to improve campaign effectiveness
- **Production Ready**: Complete with Docker support, CI/CD pipelines, monitoring, and deployment guides

### Who Should Use HyFuzz?

- **Security Researchers**: Testing IoT devices, industrial control systems, and network protocols
- **Penetration Testers**: Automated vulnerability discovery in complex distributed systems
- **QA Engineers**: Robustness testing of protocol implementations
- **Academic Researchers**: Studying fuzzing techniques and defense mechanisms
- **DevSecOps Teams**: Integrating security testing into CI/CD pipelines

## Key Features

### 🤖 Intelligent Fuzzing

- **LLM Payload Generation**: Context-aware payload creation using Mistral, Llama, GPT-4, or custom models
- **Adaptive Strategies**: Campaign strategies that learn from execution feedback
- **Protocol-Specific Templates**: Optimized payload generation for each supported protocol
- **Quality Assessment**: Automated judgment of payload effectiveness using LLM judges

### 🛡️ Defense System Integration

- **Real-Time Analysis**: Immediate defense verdict generation (monitor, investigate, block, escalate)
- **Risk Scoring**: Continuous risk assessment of execution results
- **Signal Detection**: Behavioral, signature-based, and anomaly detection
- **Event Correlation**: Cross-execution pattern recognition

### 🌐 Multi-Protocol Support

- **CoAP (Constrained Application Protocol)**: IoT device testing
- **Modbus**: Industrial control system fuzzing
- **MQTT**: Message broker and IoT gateway testing
- **HTTP/HTTPS**: Web API and service testing
- **Extensible Framework**: Easy addition of custom protocols

### 📊 Comprehensive Monitoring

- **Real-Time Dashboard**: Web-based monitoring with Server-Sent Events
- **Campaign Statistics**: Execution metrics, verdict breakdowns, judgment scores
- **Instrumentation Data**: Syscall traces, coverage information, resource usage
- **Result Aggregation**: Automated summary generation and reporting

### 🚀 Distributed Execution

- **Campaign Coordinator**: Centralized orchestration of multi-target campaigns
- **Worker Pool Management**: Scalable execution across multiple agents
- **Load Balancing**: Intelligent distribution of payloads across clients
- **Fault Tolerance**: Automatic retry and error handling

### 🔧 Developer-Friendly

- **Comprehensive API**: RESTful API for all platform operations
- **Python SDK**: Easy integration with existing tools and workflows
- **Extensive Documentation**: Detailed guides, API references, and examples
- **Testing Framework**: Integration tests, unit tests, and CI/CD pipelines

## Architecture

HyFuzz employs a distributed architecture with three main components:

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HyFuzz Platform                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              Windows Server (Control Plane)                    │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • LLM Payload Generator (Ollama/OpenAI)                      │ │
│  │  • Defense System Integrator                                  │ │
│  │  • LLM Judge & Feedback Loop                                  │ │
│  │  • Campaign Management API                                    │ │
│  │  • Web Dashboard (FastAPI + SSE)                             │ │
│  │  • Task Queue (Celery + Redis)                               │ │
│  │  • Database (SQLite/PostgreSQL)                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │               Campaign Coordinator                             │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • Multi-Protocol Orchestration                               │ │
│  │  • Server-Client Integration                                  │ │
│  │  • Result Aggregation                                         │ │
│  │  • Feedback Loop Management                                   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │           Ubuntu Client (Execution Engine)                     │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │  • Payload Execution & Sandboxing                             │ │
│  │  • Instrumentation (strace, ltrace, perf)                     │ │
│  │  • Protocol Handlers (CoAP, Modbus, MQTT, HTTP)              │ │
│  │  • Result Collection & Reporting                              │ │
│  │  • Crash Detection & Analysis                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | Technology Stack | Purpose |
|-----------|-----------------|---------|
| **Windows Server** | Python 3.11, FastAPI, SQLAlchemy, Celery | Control plane for campaign orchestration and LLM integration |
| **Ubuntu Client** | Python 3.11, instrumentation tools (strace, perf, gdb) | Payload execution engine with comprehensive instrumentation |
| **Campaign Coordinator** | Python dataclasses, async/await | Bridges server and client for distributed campaign execution |
| **LLM Integration** | Ollama, OpenAI API, Azure OpenAI | Intelligent payload generation and quality assessment |
| **Defense System** | Custom Python modules | Real-time threat analysis and verdict generation |
| **Database** | SQLite (dev), PostgreSQL (prod) | Campaign data, execution results, and analytics |
| **Task Queue** | Celery, Redis | Distributed task execution and worker management |
| **Monitoring** | FastAPI dashboard, Prometheus, Grafana | Real-time metrics and visualization |

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Quick Start

### Prerequisites

**System Requirements:**
- **Server**: Windows 10/11 or Ubuntu 22.04+ with Python 3.10+
- **Client**: Ubuntu 22.04+ with Python 3.10+
- **LLM Service**: Ollama (local) or OpenAI API key (cloud)
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB+ available space

**Software Dependencies:**
- Python 3.10 or higher (3.11 recommended)
- Git 2.30+
- Docker 24.0+ (optional, for containerized deployment)
- Make (optional, for automation tasks)

### Installation

#### Option 1: Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Run automated setup
make quickstart

# Verify installation
python scripts/health_check.py --verbose
```

The `make quickstart` command will:
1. Install all Python dependencies
2. Initialize the database with demo data
3. Run health checks
4. Display next steps

#### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Install server dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install client dependencies
cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
cd ..
python scripts/init_database.py --demo-data

# Verify installation
python scripts/health_check.py --verbose
```

### Configuration

#### 1. Configure the Server

```bash
# Copy environment template
cp HyFuzz-Windows-Server/.env.example HyFuzz-Windows-Server/.env

# Edit configuration
nano HyFuzz-Windows-Server/.env
```

**Key Configuration Options:**

```bash
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080

# LLM Configuration
OLLAMA_ENDPOINT=http://localhost:11434
DEFAULT_MODEL=mistral

# Or use OpenAI
# OPENAI_API_KEY=your-api-key-here
# DEFAULT_MODEL=gpt-4

# Database
DATABASE_URL=sqlite:///data/hyfuzz.db

# Defense System
DEFENSE_ENABLED=true
DEFENSE_MODULES=behavioral,signature,anomaly

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/server.log
```

#### 2. Configure the Client

```bash
# Copy environment template
cp HyFuzz-Ubuntu-Client/.env.example HyFuzz-Ubuntu-Client/.env

# Edit configuration
nano HyFuzz-Ubuntu-Client/.env
```

**Key Configuration Options:**

```bash
# Client Configuration
CLIENT_ID=ubuntu-client-01
SERVER_URL=http://localhost:8080

# Instrumentation
INSTRUMENTATION_ENABLED=true
INSTRUMENTATION_TOOLS=strace,perf

# Sandboxing
SANDBOX_ENABLED=true
SANDBOX_TYPE=docker

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/client.log
```

#### 3. Install and Configure Ollama (Optional)

```bash
# Download and install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull models
ollama pull mistral
ollama pull codellama
```

### Running Your First Campaign

#### Method 1: Using the Coordinator

```python
# create_campaign.py
from coordinator import FuzzingCoordinator, CampaignTarget

# Initialize coordinator
coordinator = FuzzingCoordinator(model_name="mistral")

# Define targets
targets = [
    CampaignTarget(
        name="coap-device",
        protocol="coap",
        endpoint="coap://192.168.1.100:5683"
    )
]

# Run campaign
summary = coordinator.run_campaign(targets)

# Display results
print(f"Executions: {len(summary.executions)}")
print(f"Verdict Breakdown: {summary.verdict_breakdown()}")
print(f"Average Score: {summary.average_judgment_score():.2f}")
```

```bash
# Run the campaign
python create_campaign.py
```

#### Method 2: Using the Web Dashboard

1. **Start the server**:
```bash
cd HyFuzz-Windows-Server
python scripts/start_server.py
```

2. **Start the client** (in a new terminal):
```bash
cd HyFuzz-Ubuntu-Client
python scripts/start_client.py
```

3. **Start the dashboard** (in a new terminal):
```bash
cd HyFuzz-Windows-Server
python scripts/start_dashboard.py
```

4. **Access the dashboard**: Open http://localhost:8888 in your browser

5. **Create a campaign** via the web interface

#### Method 3: Using the Makefile

```bash
# Run a demo campaign
make run-campaign

# Or run the coordinator
make run-coordinator

# Or use Docker
make docker-up
```

### Verifying the Installation

```bash
# Run health check
python scripts/health_check.py --verbose

# Run integration tests
pytest tests/ -v -m integration

# Run coordinator test
pytest tests/test_coordinator.py -v
```

**Expected Health Check Output:**
```
✓ Server: healthy
✓ Client: healthy
✓ Database: healthy
✓ LLM: healthy
✓ Defense: healthy

All systems operational!
```

For more detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md).

## Project Structure

```
HyFuzz/
├── HyFuzz-Windows-Server/       # Windows server control plane
│   ├── src/                     # Source code
│   │   ├── llm/                 # LLM integration (generation, judge)
│   │   ├── defense/             # Defense system modules
│   │   ├── protocols/           # Protocol handlers
│   │   ├── learning/            # Feedback loop implementation
│   │   └── utils/               # Utilities and helpers
│   ├── scripts/                 # Executable scripts
│   │   ├── start_server.py      # Server startup
│   │   ├── start_workers.py     # Worker pool management
│   │   ├── start_dashboard.py   # Web dashboard
│   │   └── run_fuzzing_campaign.py  # Campaign runner
│   ├── config/                  # Configuration files
│   ├── docs/                    # Server documentation
│   ├── tests/                   # Server tests
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment template
│
├── HyFuzz-Ubuntu-Client/        # Ubuntu execution client
│   ├── src/                     # Source code
│   │   ├── execution/           # Payload execution engine
│   │   ├── instrumentation/     # Instrumentation tools
│   │   ├── protocols/           # Protocol implementations
│   │   └── models/              # Data models
│   ├── scripts/                 # Executable scripts
│   │   ├── start_client.py      # Client startup
│   │   └── run_campaign.py      # Campaign execution
│   ├── config/                  # Configuration files
│   ├── docs/                    # Client documentation
│   ├── tests/                   # Client tests
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment template
│
├── coordinator/                 # Campaign coordination engine
│   ├── __init__.py              # Public API exports
│   ├── coordinator.py           # Coordination logic
│   └── README.md                # Coordinator documentation
│
├── configs/                     # Shared configuration
│   └── campaign_demo.yaml       # Demo campaign config
│
├── scripts/                     # Shared scripts
│   ├── health_check.py          # Platform health verification
│   └── init_database.py         # Database initialization
│
├── tests/                       # Integration tests
│   ├── test_coordinator.py      # Coordinator tests
│   └── test_integration.py      # Platform integration tests
│
├── docs/                        # Additional documentation
│
├── .github/                     # GitHub configuration
│   └── workflows/               # CI/CD pipelines
│       └── ci.yml               # Main CI workflow
│
├── README.md                    # This file
├── QUICKSTART.md                # Quick start guide
├── DEPLOYMENT.md                # Deployment guide
├── API.md                       # API documentation
├── ARCHITECTURE.md              # Architecture details
├── TROUBLESHOOTING.md           # Troubleshooting guide
├── CONTRIBUTING.md              # Contribution guide
├── Makefile                     # Automation tasks
├── docker-compose.yml           # Docker orchestration
├── conftest.py                  # Pytest configuration
└── .gitignore                   # Git ignore rules
```

### Key Directories Explained

- **HyFuzz-Windows-Server**: Control plane with LLM integration, defense systems, and campaign management
- **HyFuzz-Ubuntu-Client**: Execution engine with instrumentation and protocol handlers
- **coordinator**: Orchestration layer that bridges server and client components
- **configs**: Shared configuration files for campaigns and system settings
- **scripts**: Utility scripts for initialization, health checks, and maintenance
- **tests**: Comprehensive test suite for all components
- **.github/workflows**: CI/CD pipelines for automated testing and deployment

## Documentation

### Getting Started

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get up and running in 15 minutes |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local, Docker, cloud, and Kubernetes deployment |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |

### Core Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and design principles |
| [API.md](API.md) | Complete API reference for server, client, and coordinator |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guidelines for contributing to the project |

### Component Documentation

| Component | Documentation |
|-----------|---------------|
| **Server** | [HyFuzz-Windows-Server/README.md](HyFuzz-Windows-Server/README.md) |
| **Client** | [HyFuzz-Ubuntu-Client/README.md](HyFuzz-Ubuntu-Client/README.md) |
| **Coordinator** | [coordinator/README.md](coordinator/README.md) |
| **Tests** | [tests/README.md](tests/README.md) |

### Specialized Guides

| Topic | Documentation |
|-------|---------------|
| **Defense Integration** | [HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md) |
| **Instrumentation** | [HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md](HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md) |
| **Protocol Guide** | [HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md) |
| **LLM Integration** | [HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md) |
| **Feedback Loops** | [HyFuzz-Windows-Server/docs/FEEDBACK_LOOP.md](HyFuzz-Windows-Server/docs/FEEDBACK_LOOP.md) |

## Usage Examples

### Example 1: Simple CoAP Fuzzing Campaign

```python
from coordinator import FuzzingCoordinator, CampaignTarget

# Initialize coordinator with Mistral model
coordinator = FuzzingCoordinator(model_name="mistral")

# Define CoAP target
target = CampaignTarget(
    name="smart-bulb",
    protocol="coap",
    endpoint="coap://192.168.1.100:5683/light"
)

# Run campaign
summary = coordinator.run_campaign([target])

# Analyze results
print(f"Total Executions: {len(summary.executions)}")
print(f"Average Quality Score: {summary.average_judgment_score():.2f}")

for execution in summary.executions:
    if execution.defense and execution.defense.verdict == "escalate":
        print(f"High-risk payload found: {execution.payload}")
        print(f"Risk score: {execution.defense.risk_score}")
```

### Example 2: Multi-Protocol Industrial Control System Testing

```python
from coordinator import FuzzingCoordinator, CampaignTarget

coordinator = FuzzingCoordinator(model_name="gpt-4")

# Define multiple targets across protocols
targets = [
    CampaignTarget(
        name="hvac-controller",
        protocol="modbus",
        endpoint="modbus://192.168.10.50:502"
    ),
    CampaignTarget(
        name="sensor-gateway",
        protocol="mqtt",
        endpoint="mqtt://192.168.10.60:1883"
    ),
    CampaignTarget(
        name="management-api",
        protocol="http",
        endpoint="http://192.168.10.70:8080/api"
    )
]

# Run coordinated campaign
summary = coordinator.run_campaign(targets)

# Export results
import json
with open('ics_campaign_results.json', 'w') as f:
    json.dump(summary.to_dict(), f, indent=2)

# Print summary
print("Campaign Summary:")
print(f"Targets Tested: {len(targets)}")
print(f"Total Executions: {len(summary.executions)}")
print("\nVerdict Breakdown:")
for verdict, count in summary.verdict_breakdown().items():
    print(f"  {verdict}: {count}")
```

### Example 3: Using the API

```python
import requests

# Create campaign via API
response = requests.post('http://localhost:8080/api/v1/campaigns',
    headers={'X-API-Key': 'your-api-key'},
    json={
        'name': 'iot-security-assessment',
        'protocol': 'coap',
        'target': 'coap://device:5683',
        'model': 'mistral',
        'config': {'payload_count': 1000}
    }
)

campaign_id = response.json()['id']

# Start campaign
requests.post(f'http://localhost:8080/api/v1/campaigns/{campaign_id}/start',
    headers={'X-API-Key': 'your-api-key'}
)

# Monitor progress
import time
while True:
    response = requests.get(f'http://localhost:8080/api/v1/campaigns/{campaign_id}',
        headers={'X-API-Key': 'your-api-key'}
    )
    status = response.json()['status']
    if status in ['completed', 'failed']:
        break
    time.sleep(5)

# Get results
results = requests.get(f'http://localhost:8080/api/v1/campaigns/{campaign_id}/statistics',
    headers={'X-API-Key': 'your-api-key'}
).json()

print(results)
```

For more examples, see the [API documentation](API.md) and [coordinator documentation](coordinator/README.md).

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with dev tools
make install

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Code Quality

```bash
# Run linters
make lint

# Format code
make format

# Check formatting
make format-check

# Run security checks
make security
```

### Development Workflow

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and test**:
```bash
# Run tests
make test

# Run specific test
pytest tests/test_coordinator.py -v

# Run with coverage
make test-cov
```

3. **Commit changes**:
```bash
git add .
git commit -m "Description of changes"
```

4. **Push and create PR**:
```bash
git push origin feature/your-feature-name
```

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Testing

HyFuzz includes a comprehensive test suite covering unit tests, integration tests, and end-to-end tests.

### Running Tests

```bash
# Run all tests
make test

# Run integration tests only
make test-integration

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/test_coordinator.py -v

# Run tests matching pattern
pytest -k "test_coap" -v
```

### Test Coverage

Current test coverage:
- Server: 85%+
- Client: 80%+
- Coordinator: 90%+
- Integration: 75%+

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from coordinator import FuzzingCoordinator, CampaignTarget

def test_my_feature():
    """Test description."""
    coordinator = FuzzingCoordinator(model_name="test")

    # Test implementation
    assert coordinator is not None
```

For testing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md#testing).

## Deployment

HyFuzz supports multiple deployment scenarios:

### Local Development

```bash
make quickstart
```

### Docker Deployment

```bash
# Build and start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Production Deployment

```bash
# Using systemd (see DEPLOYMENT.md for setup)
sudo systemctl start hyfuzz-server
sudo systemctl start hyfuzz-workers
sudo systemctl start hyfuzz-client

# Check status
sudo systemctl status hyfuzz-server
```

### Cloud Deployment

HyFuzz supports deployment to:
- **AWS**: EC2, RDS, ElastiCache
- **Azure**: VMs, Azure Database, Azure Cache
- **GCP**: Compute Engine, Cloud SQL, Memorystore
- **Kubernetes**: Complete Helm charts and manifests

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- **Report Bugs**: Open an issue with detailed reproduction steps
- **Suggest Features**: Propose new features or improvements
- **Submit Pull Requests**: Fix bugs or implement features
- **Improve Documentation**: Help make our docs better
- **Share Experience**: Write blog posts or tutorials

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide (100 character line length)
- Write comprehensive docstrings (Google style)
- Add type hints to all functions
- Include tests for new features
- Update documentation as needed

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Code of Conduct

Please review our [Code of Conduct](HyFuzz-Windows-Server/CODE_OF_CONDUCT.md) before contributing.

## Support and Community

### Getting Help

1. **Documentation**: Start with our comprehensive documentation
2. **Troubleshooting Guide**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Issues**: Search existing GitHub issues
4. **Discussions**: Join GitHub Discussions for questions

### Reporting Issues

When reporting issues, please include:

- HyFuzz version
- Operating system and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs and error messages

### Commercial Support

For commercial support, training, or custom development:
- Email: support@hyfuzz.example.com
- Enterprise: enterprise@hyfuzz.example.com

## License

HyFuzz is released under the [MIT License](LICENSE).

### Citation

If you use HyFuzz in academic work, please cite:

```bibtex
@software{hyfuzz2024,
  title={HyFuzz: Intelligent Distributed Fuzzing Platform},
  author={HyFuzz Development Team},
  year={2024},
  url={https://github.com/your-org/HyFuzz}
}
```

For complete citation metadata, see [CITATION.cff](HyFuzz-Windows-Server/CITATION.cff).

---

## Quick Links

- **Website**: https://hyfuzz.example.com
- **Documentation**: https://docs.hyfuzz.example.com
- **GitHub**: https://github.com/your-org/HyFuzz
- **Issues**: https://github.com/your-org/HyFuzz/issues
- **Discussions**: https://github.com/your-org/HyFuzz/discussions

---

<div align="center">

**Built with ❤️ by the HyFuzz Development Team**

[⬆ Back to Top](#hyfuzz---intelligent-distributed-fuzzing-platform)

</div>
