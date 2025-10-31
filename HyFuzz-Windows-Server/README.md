# HyFuzz Server – Windows MCP Orchestrator

> Phase 3 (Stateful Defense-Aware Fuzzing) • Version 2.0.0 • Windows build

HyFuzz Server is the Windows-hosted brain of the HyFuzz distributed fuzzing ecosystem. The service exposes a Model Context Protocol (MCP) façade that coordinates Large Language Model (LLM) reasoning, knowledge fusion, adaptive fuzzing strategies, and defense-aware analytics before forwarding actionable payloads to the Ubuntu client executors.

**Repository:** `hyfuzz-server-windows`  
**Primary Platform:** Windows 10/11 (PowerShell + Python 3.9+)  
**Secondary Targets:** Windows Server 2019/2022, WSL2, or Windows-hosted VirtualBox  
**Lifecycle State:** Phase 3 complete (defense, multi-protocol, monitoring, and reporting)  
**LLM Stack:** Ollama (default) with optional OpenAI/Azure fallbacks

---

## 📋 Table of Contents

- [Overview](#overview)
- [Phase 3 Deliverables](#phase-3-deliverables)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Operational Playbooks](#operational-playbooks)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Ecosystem Topology](#ecosystem-topology)
- [API Reference](#api-reference)
- [LLM Integration](#-llm-integration)
- [Knowledge Management](#knowledge-management)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Documentation Map](#documentation-map)
- [Contributing](#contributing)
- [License](#license)
- [Security Notice](#security-notice)
- [Support](#support)

---

## 🎯 Overview

HyFuzz Server is the brain of the HyFuzz vulnerability detection framework. It implements:

- **LLM-CoT Reasoning Engine**: Chain-of-thought prompting for intelligent payload generation
- **Dual Knowledge Base**: Graph DB for symbolic knowledge + Vector DB for semantic memory
- **MCP Protocol Handler**: Bidirectional communication with Ubuntu MCP Client
- **Adaptive Learning System**: Feedback-driven optimization of fuzzing strategies
- **Protocol-Agnostic Design**: Supports multiple vulnerability types and attack vectors

The server coordinates with the Ubuntu MCP Client to execute payloads against CoAP and Modbus targets, collecting execution results and refining attack strategies through machine learning.

### Architecture Layers
```
┌─────────────────────────────────────────┐
│   MCP Server Core                       │
│   (Protocol Handler & Message Router)   │
├─────────────────────────────────────────┤
│   LLM Service Layer                     │
│   (Ollama Integration & Caching)        │
├─────────────────────────────────────────┤
│   CoT Reasoning Engine                  │
│   (Chain-of-Thought Inference)          │
├─────────────────────────────────────────┤
│   Knowledge Retrieval Layer             │
│   (Graph DB + Vector DB + Fusion)       │
├─────────────────────────────────────────┤
│   Data Models & Configuration           │
└─────────────────────────────────────────┘
```

---

## 🧱 Phase 3 Deliverables

Phase 3 finalises the Windows server feature set described in the project tree snapshot. The following subsystems are now implemented and wired into the primary MCP orchestration flow:

| Area | Key Modules | Highlights |
| ---- | ----------- | ---------- |
| Defense Intelligence | `src/defense/` (integrator, analyzers, feedback) | Correlates WAF/IDS outputs with fuzzing context and drives evasion-aware scoring. |
| Protocol Orchestration | `src/protocols/` registry + handlers | Unified factory for CoAP, Modbus, MQTT, HTTP, gRPC, and JSON-RPC pipelines with validation helpers. |
| Distributed Tasking | `src/tasks/` queue, scheduler, worker manager | Celery-ready abstraction for coordinating multiple Ubuntu clients and replay campaigns. |
| Monitoring & Telemetry | `src/monitoring/`, `src/dashboard/`, `src/reporting/` | Prometheus exporters, Grafana dashboard hooks, automated PDF/HTML report generators. |
| Security & Governance | `src/auth/`, `src/resources/`, `src/notifications/` | RBAC, API key lifecycle, quota enforcement, and multi-channel alerting. |
| Persistence & Ops | `src/migrations/`, `src/backup/`, `docker/`, `scripts/` | Database migrations, snapshot management, container entrypoints, and maintenance scripts. |

Refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for deeper component-level diagrams and dataflow explanations.

---

## ✨ Features

### Core Capabilities

- **Intelligent Exploit Generation**
  - Chain-of-Thought reasoning for attack formulation
  - Context-aware payload synthesis
  - Historical payload retrieval via semantic similarity

- **Dual Knowledge Management**
  - **Graph Database**: CVE-CWE hierarchy, protocol relationships, attack patterns
  - **Vector Database**: Embeddings of successful payloads and exploitation chains
  - **Fusion Layer**: Unified retrieval combining symbolic and semantic knowledge

- **LLM Integration**
  - Support for Ollama local models (Mistral, Llama 2, etc.)
  - Prompt optimization and caching
  - Token counting and cost estimation
  - Batch processing for efficiency

- **Feedback-Driven Adaptation**
  - Real-time performance metrics calculation
  - Automatic prompt refinement based on execution results
  - Learning-based strategy tuning
  - Defense evasion awareness

- **Multi-Transport Communication**
  - Standard I/O (stdio)
  - HTTP REST API
  - WebSocket for real-time streaming

- **Comprehensive Logging & Monitoring**
  - Structured logging with multiple levels
  - Performance metrics tracking
  - Error aggregation and analysis
  - Health check endpoints

---

## 💻 System Requirements

### Minimum Specifications

- **Operating System**: Windows 10 (Build 19041+) or Windows 11
- **Processor**: Intel i5/AMD Ryzen 5 or better (8+ cores recommended)
- **RAM**: 8GB minimum, 16GB+ recommended (for local LLM models)
- **Storage**: 10GB free space (including LLM model storage)
- **Python**: 3.9, 3.10, or 3.11

### Software Dependencies

- **Ollama**: 0.1.0+ (for local LLM inference)
  - Download from: https://ollama.ai
  - Models: mistral, neural-chat, dolphin-mixtral (recommended)
  
- **Python Packages**: See [requirements.txt](#dependencies)

- **Optional Services**:
  - PostgreSQL 12+ (for persistent knowledge storage)
  - Redis 6+ (for caching layer)
  - Milvus (for advanced vector DB operations)

### Network Requirements

- Local network access to Ubuntu MCP Client (default: TCP 5000)
- Internet access for model downloads (one-time)
- No firewall blocking on configured ports

---

## 📦 Installation

### Step 1: Prerequisites
```bash
# Install Python 3.9+
python --version  # Verify Python installation

# Install Ollama
# Download from https://ollama.ai and follow installation guide
ollama --version
```

### Step 2: Clone Repository
```bash
git clone https://github.com/your-org/hyfuzz-server-windows.git
cd hyfuzz-server-windows
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) prefix)
```

### Step 4: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 5: Setup Ollama Models
```bash
# Start Ollama service
ollama serve

# In a new terminal, pull required model
ollama pull mistral
# or
ollama pull neural-chat

# Verify model installation
ollama list
```

### Step 6: Initialize Configuration
```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings
# Open .env in text editor and configure:
# - LLM_MODEL_NAME=mistral
# - OLLAMA_API_URL=http://localhost:11434
# - SERVER_HOST=0.0.0.0
# - SERVER_PORT=5000

# Generate initial data files
python scripts/setup_env.py
```

### Step 7: Verify Installation
```bash
# Run health check
python scripts/health_check.py

# Expected output: All checks passed ✓
```

---

## 🚀 Quick Start

### Basic Server Startup
```bash
# Activate virtual environment (if not already active)
venv\Scripts\activate

# Start the MCP server
python -m src

# Or use the convenience script
python scripts/start_server.py

# Expected output:
# [INFO] MCP Server started on 0.0.0.0:5000
# [INFO] LLM Service initialized (Model: mistral)
# [INFO] Knowledge base loaded (CWE: 5000+, CVE: 100000+)
# [INFO] Waiting for client connections...
```

### Test Connection from Client
```bash
# From Ubuntu MCP Client machine
python scripts/test_connection.py --host <server-ip> --port 5000

# Expected output:
# Connection: OK ✓
# LLM Service: OK ✓
# Knowledge Base: OK ✓
# Ready for fuzzing: OK ✓
```

### Generate Payload Example
```python
# Interactive payload generation test
python scripts/test_mcp.py

# Example interaction:
# Enter CWE ID: 79
# Enter target protocol: coap
# Enter context: unvalidated user input in URI
# 
# Generated Payload:
# {
#   "cwe_id": "CWE-79",
#   "reasoning": "XSS vulnerability in CoAP URI...",
#   "payload": "coap://target/admin/%3Cscript%3Ealert(1)%3C/script%3E",
#   "success_probability": 0.82
# }
```

---

## 🛠️ Operational Playbooks

### Daily Operations (PowerShell)

```powershell
# 1. Launch the server and background workers
$env:PYTHONPATH = (Resolve-Path .).Path
venv\Scripts\Activate.ps1
python scripts\start_server.py

# 2. Tail the aggregated logs in a separate terminal
Get-Content .\logs\server.log -Wait

# 3. (Optional) Start the dashboard for real-time metrics
python scripts\start_dashboard.py --host 0.0.0.0 --port 8080
```

### Distributed Campaign Rollout

```powershell
# Start Celery-style task workers on the Windows host
python scripts\start_workers.py --pool threads --concurrency 8

# Trigger a distributed fuzzing campaign
python scripts\run_fuzzing_campaign.py ^
  --strategy adaptive ^
  --targets config\example_configs\config_distributed.yaml ^
  --sync-results

# Monitor queued jobs and client heartbeats
python scripts\monitor_tasks.py --interval 10
```

### Maintenance & Recovery

```powershell
# Rotate logs older than 14 days
python scripts\maintenance\rotate_logs.py --retention-days 14

# Snapshot configuration, database, and results artifacts
python scripts\backup_system.py --output data\backups\$(Get-Date -Format 'yyyyMMdd_HHmm')

# Restore the latest snapshot (dry run supported)
python scripts\restore_system.py --snapshot <path> --dry-run
```

### VirtualBox / WSL2 Checklist

- Ensure the Ubuntu client VM or WSL2 distribution exposes TCP ports 5000 (MCP) and 5672/6379 (if using RabbitMQ/Redis).
- Share a host-only adapter so Windows and Ubuntu can resolve each other via static IPs or DNS entries.
- When migrating to Windows 11, export the `.env` file and the `data/` knowledge cache; import them after re-provisioning VirtualBox.
- Enable virtualization extensions (VT-x/AMD-V) in BIOS for stable instrumentation performance on the guest clients.

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# ============ Server Configuration ============
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
SERVER_LOG_LEVEL=INFO
SERVER_WORKERS=4

# ============ LLM Configuration ============
LLM_PROVIDER=ollama                    # or 'azure', 'openai'
LLM_MODEL_NAME=mistral                 # Model to use
OLLAMA_API_URL=http://localhost:11434  # Ollama service URL
LLM_TEMPERATURE=0.7                    # Creativity (0.0-1.0)
LLM_MAX_TOKENS=2048                    # Max response length
LLM_CACHE_ENABLED=true                 # Enable caching
LLM_CACHE_TTL=3600                     # Cache TTL in seconds

# ============ Knowledge Base Configuration ============
KNOWLEDGE_BASE_PATH=./data/knowledge_cache
GRAPH_DB_PATH=./data/knowledge_cache/graph_db.pkl
VECTOR_DB_PATH=./data/knowledge_cache/vector_db.pkl
CWE_DATA_FILE=./data/cwe_data.json
CVE_DATA_FILE=./data/cve_data.json
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ============ Database Configuration ============
DB_ENABLE=false                        # Enable database storage
DB_TYPE=sqlite                         # sqlite, postgresql
DB_PATH=./data/hyfuzz.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=hyfuzz
DB_PASSWORD=
DB_NAME=hyfuzz_db

# ============ Cache Configuration ============
CACHE_BACKEND=memory                   # memory, redis
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600

# ============ Logging Configuration ============
LOG_FILE=./logs/server.log
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                        # json, standard
LOG_MAX_SIZE=10485760                  # 10MB
LOG_BACKUP_COUNT=5

# ============ Performance Tuning ============
BATCH_SIZE=32
EMBEDDING_CACHE_SIZE=10000
QUERY_TIMEOUT=30
CONCURRENT_REQUESTS=10
```

### Configuration Files

**config/default_config.yaml**: Default server configuration
```yaml
server:
  host: "0.0.0.0"
  port: 5000
  timeout: 30
  max_connections: 100

llm:
  provider: "ollama"
  model: "mistral"
  temperature: 0.7
  max_tokens: 2048
  cache_enabled: true

knowledge:
  graph_db_enabled: true
  vector_db_enabled: true
  fusion_strategy: "hybrid"
  retrieval_top_k: 5

security:
  enable_authentication: false
  enable_rate_limiting: true
  rate_limit_requests: 100
  rate_limit_window: 60
```

---

## 🏛️ Architecture

### Component Overview
```
┌─────────────────────────────────────────────────┐
│          MCP Server (server.py)                 │
│  - Protocol handling                            │
│  - Request routing                              │
│  - Session management                           │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│  LLM    │  │Knowledge │  │ Capability│
│Service  │  │Retrieval │  │ Manager  │
│(llm.py)│  │(krw/)   │  │(mcp_core)│
└────┬────┘  └────┬─────┘  └─────┬────┘
     │            │              │
     ▼            ▼              ▼
┌──────────────────────────────────┐
│    Core Processing Modules       │
├──────────────────────────────────┤
│ • CoT Engine (cot_engine.py)    │
│ • Prompt Builder                │
│ • Embedding Manager             │
│ • Cache Manager                 │
└──────────────────────────────────┘
     │            │
     ▼            ▼
┌──────────────┐  ┌────────────────┐
│ Graph DB     │  │  Vector DB     │
│ (CWE/CVE)    │  │  (Payloads)    │
└──────────────┘  └────────────────┘
```

### Data Flow

1. **Initialization**: Load knowledge base, initialize LLM, prepare caches
2. **Client Request**: Receive fuzzing request from Ubuntu client
3. **Knowledge Retrieval**: Query Graph DB + Vector DB with fusion layer
4. **CoT Reasoning**: Generate reasoning chain via LLM
5. **Payload Generation**: Create exploit payload based on reasoning
6. **Response**: Send payload + reasoning chain to client
7. **Feedback Loop**: Receive execution results and refine strategies
8. **Learning**: Update embeddings and knowledge cache

---

## 🌐 Ecosystem Topology

```
         ┌───────────────────────────┐
         │  Windows Host (Server)    │
         │  • MCP API / WebSockets   │
         │  • LLM + Knowledge Fusion │
         │  • Defense Integrations   │
         └────────────┬──────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
┌───────▼────────┐         ┌─────────▼────────┐
│ Ubuntu Client  │         │ Ubuntu Client    │
│ (VirtualBox/   │  ...    │ (Bare-metal/WSL) │
│  Physical)     │         │                   │
│ • Payload Exec │         │ • Instrumentation │
│ • Coverage     │         │ • Crash Analysis  │
└───────┬────────┘         └─────────┬────────┘
        │                              │
        └────────────┬─────────────────┘
                     │ Results & Metrics
                     ▼
         ┌───────────────────────────┐
         │ Shared Storage / DB       │
         │ • PostgreSQL / SQLite     │
         │ • Redis Cache             │
         │ • Backup Snapshots        │
         └───────────────────────────┘
```

- **Transport Mix**: MCP over stdio for local tooling, HTTPS/WebSocket for remote clients, RabbitMQ/Redis (optional) for distributed queueing.
- **Observability Loop**: Metrics streamed to Prometheus exporters (`src/monitoring/metrics_collector.py`) and visualised via the dashboard web server.
- **Defense Feedback**: WAF/IDS telemetry is ingested into `src/defense/log_aggregator.py` and feeds back into the LLM judge to steer payload selection.

---

## 📡 API Reference

### Transport Protocols

The server supports multiple communication methods:

#### Standard I/O (stdio)
```bash
# Used for local process communication
python -m src --transport stdio
```

#### HTTP REST API
```bash
# RESTful API on http://localhost:5000

# Health check
GET /health

# Payload generation
POST /api/v1/payloads/generate
Content-Type: application/json

{
  "cwe_id": "CWE-79",
  "protocol": "coap",
  "target_info": {
    "version": "1.0",
    "capabilities": ["OBSERVE"]
  },
  "execution_context": {
    "successful_payloads": [],
    "failed_payloads": []
  }
}

# Response
{
  "payload": "coap://target/uri?q=<script>alert(1)</script>",
  "reasoning_chain": ["Step 1: ...", "Step 2: ..."],
  "confidence_score": 0.82,
  "cve_references": ["CVE-2023-XXXX"],
  "success_probability": 0.78
}
```

#### WebSocket API
```javascript
// Real-time streaming
ws = new WebSocket('ws://localhost:5000/api/v1/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Reasoning step:', data.step);
  console.log('Payload:', data.payload);
};
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health status |
| GET | `/api/v1/status` | Detailed system status |
| POST | `/api/v1/payloads/generate` | Generate exploit payload |
| POST | `/api/v1/payloads/refine` | Refine payload strategy |
| GET | `/api/v1/knowledge/cwe/{id}` | Get CWE information |
| GET | `/api/v1/knowledge/cve/{id}` | Get CVE information |
| POST | `/api/v1/feedback` | Submit execution feedback |
| GET | `/api/v1/metrics` | Get performance metrics |

---

## 🤖 LLM Integration

### Supported Models

The server works with any Ollama-compatible model:
```bash
# Download models
ollama pull mistral                 # Fast, good quality (7B)
ollama pull neural-chat            # Optimized for chat (7B)
ollama pull dolphin-mixtral        # Specialized (8x7B)
ollama pull llama2-uncensored      # Uncensored variant (7B)
ollama pull openhermes-2.5-mistral # Multi-task (7B)
```

### Configuration
```python
# In .env or config.yaml
LLM_MODEL_NAME=mistral
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
LLM_TEMPERATURE=0.7              # Lower = more deterministic
LLM_TOP_P=0.95                   # Nucleus sampling
LLM_MAX_TOKENS=2048              # Response length limit
```

### Prompt Engineering

The server uses sophisticated prompt templates:
```python
# Example: XSS detection prompt
prompt = """
You are a security expert analyzing protocol vulnerabilities.

Target: {protocol}
Vulnerability Type: {cwe_description}
Known patterns: {similar_payloads}

Reasoning steps:
1. Analyze the vulnerability mechanism
2. Identify injection points
3. Formulate exploitation strategy
4. Generate proof-of-concept payload

Payload format for {protocol}: {protocol_specs}

Generate a crafted payload:
"""
```

---

## 📚 Knowledge Management

### Graph Database (CWE/CVE Hierarchy)
```python
# Knowledge structure
{
  "CWE-79": {
    "title": "Improper Neutralization of Input During Web Page Generation",
    "parent": "CWE-116",
    "related_cves": ["CVE-2023-1234", "CVE-2023-5678"],
    "attack_patterns": ["CAPEC-86", "CAPEC-87"],
    "affected_protocols": ["HTTP", "CoAP"],
    "remediation": "Sanitize all user inputs..."
  }
}
```

### Vector Database (Semantic Search)
```python
# Payload embeddings for similarity search
{
  "payload_id": "coap_xss_001",
  "payload": "coap://target/%3Cscript%3E...",
  "embedding": [0.23, -0.15, 0.89, ...],  # 384-dim vector
  "success_rate": 0.82,
  "cwe_id": "CWE-79",
  "protocol": "coap"
}
```

### Retrieval Strategy
```
Query: Find similar payloads for CoAP XSS attack
           ↓
    1. Symbolic (Graph DB)
       - Find CWE-79 attacks
       - Filter by CoAP protocol
       - Get candidate payloads
           ↓
    2. Semantic (Vector DB)
       - Embed query
       - Find top-5 similar payloads
       - Rank by relevance
           ↓
    3. Fusion Layer
       - Combine results
       - Re-rank by score
       - Return top-k results
```

---

## 👨‍💻 Development Guide

### Project Structure
```
src/
├── mcp_server/          # Core MCP protocol handler
├── llm/                 # LLM integration layer
├── knowledge/           # Knowledge base management
├── models/              # Data models
├── config/              # Configuration management
├── utils/               # Utility functions
└── api/                 # REST API handlers
```

### Adding a New Feature
```python
# 1. Define data model (models/)
class MyFeatureRequest(BaseModel):
    param1: str
    param2: int

# 2. Implement logic (appropriate module/)
class MyFeatureHandler:
    async def process(self, request: MyFeatureRequest):
        # Implementation
        pass

# 3. Register endpoint (api/routes.py)
@app.post("/api/v1/my-feature")
async def my_feature_endpoint(request: MyFeatureRequest):
    handler = MyFeatureHandler()
    return await handler.process(request)

# 4. Add tests (tests/unit/)
def test_my_feature():
    # Test implementation
    pass
```

### Code Style

- **Language**: English for all comments and docstrings
- **Format**: PEP 8 compliant
- **Linting**: `pylint`, `flake8`, `black`
- **Type Hints**: Use type annotations for all functions
```python
# Good example
async def generate_payload(
    cwe_id: str,
    protocol: str,
    context: Dict[str, Any]
) -> PayloadResponse:
    """
    Generate an exploit payload using CoT reasoning.
    
    Args:
        cwe_id: Common Weakness Enumeration identifier
        protocol: Target protocol (coap, modbus)
        context: Additional context for generation
        
    Returns:
        PayloadResponse with generated payload and reasoning chain
        
    Raises:
        ValueError: If CWE ID not found
        TimeoutError: If LLM inference exceeds timeout
    """
    # Implementation
    pass
```

### Running Tests
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_cot_engine.py -v
```

### Performance Profiling
```bash
# Profile server performance
python scripts/benchmark.py

# Memory usage analysis
python -m memory_profiler src/mcp_server/server.py
```

---

## 🧪 Testing

### Test Suite Overview
```
tests/
├── unit/                      # Unit tests (isolated)
│   ├── test_llm_client.py
│   ├── test_cot_engine.py
│   ├── test_knowledge_loader.py
│   └── ...
├── integration/               # Integration tests
│   ├── test_llm_pipeline.py
│   ├── test_mcp_protocol.py
│   └── test_end_to_end.py
├── performance/               # Performance tests
│   └── test_server_perf.py
└── fixtures/                  # Test data & mocks
    ├── mock_llm.py
    └── mock_data.py
```

### Running Tests
```bash
# Run all tests
make test

# Run specific category
pytest tests/unit -v
pytest tests/integration -v

# With coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test
pytest tests/unit/test_cot_engine.py::test_reasoning_chain -v
```

### Test Coverage Goals

- **Minimum**: 80% overall coverage
- **Critical modules**: 95% (llm_service, cot_engine)
- **Utils**: 70% (less critical)

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "Connection refused" from Client
```
Error: Failed to connect to server at localhost:5000
```

**Solution:**
```bash
# Check server is running
netstat -ano | findstr :5000

# Verify firewall rules
# Windows Defender Firewall → Allow an app

# Check .env configuration
# Ensure SERVER_HOST and SERVER_PORT match client expectations
```

#### Issue: "Ollama service not available"
```
Error: HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded
```

**Solution:**
```bash
# Start Ollama service
ollama serve

# Verify Ollama is running
ollama list

# Check OLLAMA_API_URL in .env
OLLAMA_API_URL=http://localhost:11434
```

#### Issue: "Out of memory" during LLM inference
```
Error: CUDA out of memory or CPU memory exhausted
```

**Solution:**
```bash
# Reduce model size
ollama pull mistral        # 7B parameter model

# Reduce batch size
BATCH_SIZE=1  # In .env

# Use quantized model
ollama pull mistral:q4  # 4-bit quantized
```

#### Issue: Knowledge base won't load
```
Error: Failed to load knowledge base from ./data/knowledge_cache
```

**Solution:**
```bash
# Regenerate knowledge base
python scripts/setup_env.py

# Or manually download
python -c "from src.knowledge import KnowledgeLoader; KnowledgeLoader.initialize()"

# Verify files exist
dir .\data\knowledge_cache\
```

### Debug Mode
```bash
# Enable debug logging
set LOG_LEVEL=DEBUG

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
python -m src --debug
```

### Performance Optimization
```bash
# Enable caching
LLM_CACHE_ENABLED=true
CACHE_BACKEND=redis

# Increase workers
SERVER_WORKERS=8

# Tune batch processing
BATCH_SIZE=32

# Monitor performance
python scripts/benchmark.py
```

---

## 📚 Documentation Map

| Guide | Description | When to Use |
| ----- | ----------- | ----------- |
| [docs/SETUP.md](docs/SETUP.md) | End-to-end Windows installation (PowerShell + VirtualBox notes). | First-time provisioning or migrating machines. |
| [docs/API.md](docs/API.md) | REST + MCP endpoint reference with payload schemas. | Building automation or integrating external tooling. |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Deep dive into core services, data stores, and async flows. | Designing new modules or auditing data paths. |
| [docs/DEFENSE_INTEGRATION.md](docs/DEFENSE_INTEGRATION.md) | How defense signals inform the LLM judge and feedback loop. | Tuning IDS/WAF correlation or adding new defense sources. |
| [docs/PROTOCOL_GUIDE.md](docs/PROTOCOL_GUIDE.md) | Protocol registry, handshake flows, mutation strategies. | Extending coverage to new industrial/IoT protocols. |
| [docs/DISTRIBUTED_FUZZING.md](docs/DISTRIBUTED_FUZZING.md) | Task queue topology, worker pools, failure recovery. | Operating large fuzzing campaigns across multiple clients. |
| [docs/REPORTING_GUIDE.md](docs/REPORTING_GUIDE.md) | Report templates, scheduling, and export automation. | Creating stakeholder deliverables or scheduled summaries. |
| [docs/MONITORING_GUIDE.md](docs/MONITORING_GUIDE.md) | Metrics catalog and dashboard instructions. | Setting up Prometheus/Grafana or custom alerts. |
| [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) | Model selection, prompt strategies, caching policies. | Switching LLM providers or optimising inference costs. |

Complementary repositories:

- **HyFuzz Client (Ubuntu):** Execution agents and instrumentation – https://github.com/your-org/hyfuzz-client-ubuntu
- **HyFuzz Specifications:** Shared protocol schemas and payload dictionaries – https://github.com/your-org/hyfuzz-specs

Further reading: Chain-of-Thought Prompting (Wei et al., 2022), Retrieval-Augmented Generation (Guu et al., 2020), Coverage-Guided Fuzzing (Böhme et al., 2021).

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow code style guidelines (see Development Guide)
4. Write tests for new functionality
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-org/hyfuzz-server-windows.git
cd hyfuzz-server-windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Make changes and test
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 HyFuzz Contributors

---

## 📞 Support

### Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **Email**: support@hyfuzz.ai

### Reporting Bugs

Please include:
- Python version: `python --version`
- OS and version: Windows 10/11
- Error message: Full traceback
- Steps to reproduce: Clear instructions
- Expected behavior: What should happen

Example bug report:
```
Title: LLM Service fails with timeout on large payloads

Environment:
- Python: 3.9.13
- OS: Windows 11 (22H2)
- Server Version: 1.0.0

Reproduction:
1. Start server with mistral model
2. Send payload generation request with large context
3. Wait for response

Error:
TimeoutError: LLM inference exceeded 30 second limit

Expected:
Should generate payload or return timeout error gracefully
```

---

## 🗺️ Roadmap

### Phase 1 ✅ Complete
- [x] MCP protocol foundation
- [x] Initial LLM-assisted payload generation
- [x] HTTP + WebSocket transports

### Phase 2 ✅ Complete
- [x] Chain-of-Thought reasoning engine
- [x] Dual knowledge base (graph + vector)
- [x] Feedback loop scaffolding and telemetry hooks

### Phase 3 ✅ Complete
- [x] Defense-aware judging & analytics pipeline
- [x] Distributed tasking + monitoring dashboard
- [x] Protocol expansion (CoAP, Modbus, MQTT, HTTP, gRPC, JSON-RPC)
- [x] Reporting, notifications, and backup automation

### Phase 4 🚧 Planned
- [ ] Hardware-in-the-loop fuzzing adapters
- [ ] Automated campaign risk scoring for executive reports
- [ ] Fine-tuned local LLM models for specific protocol families
- [ ] Continuous compliance auditing and signed artefact delivery

---

## 👥 Authors

**HyFuzz Development Team**

- **Lead**: [Your Name] - Architecture & LLM Integration
- **Contributors**: [Contributors list]

---

## 🙏 Acknowledgments

- MITRE for CWE/CVE data
- Ollama for local LLM inference
- OpenAI for inspiration from few-shot prompting
- Research community for fuzzing methodologies

---

## 📊 Statistics

- **Source footprint**: ~28,000 lines (Phase 3 aggregate across src/, tests/, docs/).
- **Automated checks**: CI workflows cover linting, unit/integration/perf suites, dependency scanning.
- **Knowledge assets**: >5,000 CWE nodes, >100,000 CVE mappings, on-disk embeddings cache shipped in `data/knowledge_cache/`.
- **Operational scripts**: 30+ automation helpers under `scripts/` (provisioning, monitoring, maintenance).

---

## 🔐 Security Notice

This platform is provided for sanctioned security testing, red-team simulation, and research within authorized environments only. Ensure written approval from system owners before executing any fuzzing or exploitation workflow.

**Disclaimer:** Software is supplied “as is”, without warranties or guarantees. Operators bear responsibility for compliance with all applicable laws, regulations, and organizational policies.

---

**Last Updated:** 2025-01-27  
**Version:** 2.0.0 (Phase 3 complete)  
**Status:** Stable operations with ongoing Phase 4 planning  
**Project URL:** https://github.com/your-org/hyfuzz-server-windows
