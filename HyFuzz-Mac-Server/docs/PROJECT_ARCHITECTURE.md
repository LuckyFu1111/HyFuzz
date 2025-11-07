# HyFuzz Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Principles](#design-principles)
- [Scalability](#scalability)
- [Security Architecture](#security-architecture)
- [Extension Points](#extension-points)

## Overview

HyFuzz is designed as a distributed intelligent fuzzing platform with three primary architectural layers:

1. **Control Plane** (Windows Server): Centralized campaign orchestration, LLM integration, and defense coordination
2. **Coordination Layer** (Campaign Coordinator): Multi-protocol orchestration and result aggregation
3. **Execution Plane** (Ubuntu Client): Payload execution with comprehensive instrumentation

### Architecture Goals

- **Modularity**: Independent, loosely-coupled components
- **Scalability**: Horizontal scaling across multiple execution agents
- **Extensibility**: Plugin-based architecture for protocols and defense modules
- **Reliability**: Fault-tolerant execution with automatic retry
- **Observability**: Comprehensive logging, monitoring, and metrics

## System Architecture

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        External Services                          │
├───────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Ollama    │  │OpenAI/Azure  │  │  PostgreSQL  │           │
│  │   (Local)    │  │    (Cloud)   │  │  (Optional)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│                   HyFuzz Control Plane (Windows Server)            │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     API Layer                                │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  • REST API (FastAPI)                                       │ │
│  │  • MCP Server Protocol                                      │ │
│  │  • WebSocket API                                            │ │
│  │  • Dashboard (Server-Sent Events)                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Business Logic Layer                       │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐ │ │
│  │  │   Campaign    │  │   LLM Judge   │  │   Feedback     │ │ │
│  │  │  Management   │  │  & Generator  │  │     Loop       │ │ │
│  │  └───────────────┘  └───────────────┘  └────────────────┘ │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐ │ │
│  │  │   Defense     │  │   Protocol    │  │   Task Queue   │ │ │
│  │  │  Integrator   │  │    Factory    │  │   Management   │ │ │
│  │  └───────────────┘  └───────────────┘  └────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Data Layer                                │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  • SQLAlchemy ORM                                           │ │
│  │  • SQLite/PostgreSQL                                        │ │
│  │  • Redis (Cache & Task Queue)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│                  Campaign Coordinator                              │
├───────────────────────────────────────────────────────────────────┤
│  • Multi-Protocol Orchestration                                   │
│  • Server-Client Integration Bridge                               │
│  • Result Aggregation & Analysis                                  │
│  • Feedback Loop Coordination                                     │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│            HyFuzz Execution Plane (Ubuntu Clients)                 │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Execution Layer                             │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  • Payload Orchestrator                                     │ │
│  │  • Protocol Handlers (CoAP, Modbus, MQTT, HTTP)            │ │
│  │  • Sandboxing Engine (Docker/Native)                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Instrumentation Layer                        │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  • System Call Tracing (strace)                             │ │
│  │  • Library Call Tracing (ltrace)                            │ │
│  │  • Performance Analysis (perf)                              │ │
│  │  • Crash Detection (GDB integration)                        │ │
│  │  • Coverage Tracking                                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Result Collection                           │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  • Execution Result Packaging                               │ │
│  │  • Crash Report Generation                                  │ │
│  │  • Instrumentation Data Aggregation                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   LLM        │◄────────┤   Windows    │────────►│  Campaign    │
│  Provider    │         │   Server     │         │ Coordinator  │
└──────────────┘         └──────────────┘         └──────────────┘
                                │                         │
                                │ Campaign Requests       │
                                ▼                         ▼
                         ┌──────────────┐         ┌──────────────┐
                         │   Defense    │         │    Ubuntu    │
                         │   System     │         │   Clients    │
                         └──────────────┘         └──────────────┘
                                │                         │
                                └─────────┬───────────────┘
                                          │
                                          ▼
                                  ┌──────────────┐
                                  │   Database   │
                                  │   (Results)  │
                                  └──────────────┘
```

## Component Architecture

### Windows Server Architecture

#### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      Windows Server                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Presentation Layer (API/UI)                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • FastAPI REST API                                    │ │
│  │  • WebSocket Handler                                   │ │
│  │  • Dashboard (SSE)                                     │ │
│  │  • MCP Server                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Application Layer                                      │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  ┌──────────────┐    ┌──────────────┐               │ │
│  │  │  Campaign    │    │  LLM         │               │ │
│  │  │  Manager     │    │  Integration │               │ │
│  │  └──────────────┘    └──────────────┘               │ │
│  │  ┌──────────────┐    ┌──────────────┐               │ │
│  │  │  Defense     │    │  Feedback    │               │ │
│  │  │  System      │    │  Loop        │               │ │
│  │  └──────────────┘    └──────────────┘               │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Domain Layer                                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Protocol Models                                     │ │
│  │  • Defense Models                                      │ │
│  │  • Campaign Models                                     │ │
│  │  • Execution Models                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Infrastructure Layer                                   │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Database Access (SQLAlchemy)                        │ │
│  │  • Task Queue (Celery)                                 │ │
│  │  • Caching (Redis)                                     │ │
│  │  • External Service Clients                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### Key Modules

**LLM Integration** (`src/llm/`):
- `payload_generator.py`: LLM-driven payload generation
- `llm_judge.py`: Execution quality assessment
- `llm_client.py`: Unified interface for Ollama/OpenAI/Azure

**Defense System** (`src/defense/`):
- `defense_integrator.py`: Defense module orchestration
- `defense_models.py`: Defense data structures
- `behavioral_defense.py`: Behavioral analysis
- `signature_defense.py`: Signature-based detection
- `anomaly_defense.py`: Anomaly detection

**Protocol Framework** (`src/protocols/`):
- `base_protocol.py`: Abstract protocol interface
- `protocol_registry.py`: Protocol registration system
- `protocol_factory.py`: Protocol handler instantiation
- `coap_protocol.py`, `modbus_protocol.py`, etc.: Specific implementations

**Feedback Loop** (`src/learning/`):
- `feedback_loop.py`: Learning from execution results
- `knowledge_base.py`: Historical data management

### Ubuntu Client Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Ubuntu Client                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Execution Engine                                       │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Orchestrator (request queue management)             │ │
│  │  • Protocol Executors (CoAP, Modbus, MQTT, HTTP)      │ │
│  │  • Sandbox Manager (Docker/Native isolation)           │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Instrumentation Engine                                 │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • System Call Tracer (strace wrapper)                 │ │
│  │  • Library Call Tracer (ltrace wrapper)                │ │
│  │  • Performance Profiler (perf integration)             │ │
│  │  • Coverage Analyzer                                   │ │
│  │  • Crash Detector                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Result Collection                                      │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Execution Result Builder                            │ │
│  │  • Instrumentation Data Aggregator                     │ │
│  │  • Server Communication (HTTP client)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Campaign Coordinator Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Campaign Coordinator                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FuzzingCoordinator                                     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  Initialization:                                       │ │
│  │    • PayloadGenerator (from server)                    │ │
│  │    • ProtocolFactory (from server)                     │ │
│  │    • DefenseIntegrator (from server)                   │ │
│  │    • LLMJudge (from server)                            │ │
│  │    • FeedbackLoop (from server)                        │ │
│  │    • Orchestrator (from client)                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Campaign Execution Flow                                │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  1. Plan Requests (generate payloads)                  │ │
│  │  2. Queue Execution (send to clients)                  │ │
│  │  3. Collect Results (aggregate responses)              │ │
│  │  4. Defense Analysis (process verdicts)                │ │
│  │  5. LLM Judgment (assess quality)                      │ │
│  │  6. Feedback Update (learn from results)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Data Models                                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • CampaignTarget                                      │ │
│  │  • ExecutionDetail                                     │ │
│  │  • CampaignRunSummary                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Campaign Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Campaign Creation                            │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  User/API Request ─────► Campaign Manager                    │
│    • Campaign name, protocol, targets                        │
│    • Configuration (payload count, model, strategy)          │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Campaign Coordinator                                         │
│    1. Load targets ────► CampaignTarget objects              │
│    2. Initialize components (LLM, Defense, Feedback)         │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Payload Generation Loop (for each target)                   │
│    ┌─────────────────────────────────────────────────┐      │
│    │  1. LLM Generator                                │      │
│    │     • Context: protocol + target + feedback      │      │
│    │     • Output: raw payload string                 │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  2. Protocol Handler                             │      │
│    │     • Validate payload                           │      │
│    │     • Apply protocol-specific templates          │      │
│    │     • Generate request parameters                │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  3. Create ExecutionDetail                       │      │
│    │     • Link: target, payload, parameters          │      │
│    └─────────────────────────────────────────────────┘      │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Execution Distribution                                       │
│    • Coordinator ────► Ubuntu Clients (via Orchestrator)     │
│    • Payload queue management                                │
│    • Load balancing across clients                           │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Client-Side Execution (for each payload)                    │
│    ┌─────────────────────────────────────────────────┐      │
│    │  1. Protocol Executor                            │      │
│    │     • Parse request parameters                   │      │
│    │     • Execute payload against target             │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  2. Instrumentation                              │      │
│    │     • strace: syscall capture                    │      │
│    │     • ltrace: library call capture               │      │
│    │     • perf: performance metrics                  │      │
│    │     • Crash detection                            │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  3. Result Collection                            │      │
│    │     • Exit code, stdout, stderr                  │      │
│    │     • Instrumentation data                       │      │
│    │     • Execution time                             │      │
│    │     • Return ExecutionResult                     │      │
│    └─────────────────────────────────────────────────┘      │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Server-Side Analysis                                         │
│    ┌─────────────────────────────────────────────────┐      │
│    │  1. Defense System                               │      │
│    │     • Create DefenseEvent from execution         │      │
│    │     • Generate DefenseSignal                     │      │
│    │     • Process through defense modules            │      │
│    │     • Output: DefenseResult (verdict, risk)      │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  2. LLM Judge                                    │      │
│    │     • Analyze payload effectiveness              │      │
│    │     • Generate quality score (0.0-1.0)           │      │
│    │     • Output: Judgment (score, reasoning)        │      │
│    ├─────────────────────────────────────────────────┤      │
│    │  3. Feedback Loop                                │      │
│    │     • Collect: protocol, score, verdict          │      │
│    │     • Update feedback history                    │      │
│    │     • Influence next payload generation          │      │
│    └─────────────────────────────────────────────────┘      │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Result Aggregation                                           │
│    • All ExecutionDetails ────► CampaignRunSummary           │
│    • Statistics: verdict breakdown, average scores           │
│    • Feedback history compilation                            │
│    • Database persistence                                    │
└───────┬──────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│  Reporting                                                    │
│    • API response / Dashboard update                         │
│    • JSON export                                             │
│    • Notification triggers (if configured)                   │
└──────────────────────────────────────────────────────────────┘
```

### Data Models

#### Database Schema

```sql
-- Campaigns table
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    protocol TEXT NOT NULL,
    target TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, running, completed, failed
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    config JSON
);

-- Payloads table
CREATE TABLE payloads (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    payload_data TEXT NOT NULL,
    generated_at TIMESTAMP,
    generation_model TEXT,
    generation_parameters JSON
);

-- Executions table
CREATE TABLE executions (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    payload_id INTEGER REFERENCES payloads(id),
    status TEXT NOT NULL,
    executed_at TIMESTAMP,
    execution_time_ms INTEGER,
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    crash_detected BOOLEAN,
    instrumentation_data JSON
);

-- Defense results table
CREATE TABLE defense_results (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER REFERENCES executions(id),
    verdict TEXT NOT NULL,  -- monitor, investigate, block, escalate
    risk_score REAL,
    signals JSON,
    events JSON,
    created_at TIMESTAMP
);

-- Judgments table
CREATE TABLE judgments (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER REFERENCES executions(id),
    score REAL,
    reasoning TEXT,
    model TEXT,
    criteria JSON,
    created_at TIMESTAMP
);

-- Feedback history table
CREATE TABLE feedback_history (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    feedback_entry TEXT,
    created_at TIMESTAMP
);

-- Protocol coverage table
CREATE TABLE protocol_coverage (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id),
    protocol TEXT,
    state_name TEXT,
    transition_name TEXT,
    hit_count INTEGER,
    first_hit_at TIMESTAMP,
    last_hit_at TIMESTAMP
);
```

## Technology Stack

### Server (Windows/Linux)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI 0.100+ | REST API, WebSocket, SSE |
| **ORM** | SQLAlchemy 2.0+ | Database abstraction |
| **Database** | SQLite (dev), PostgreSQL 14+ (prod) | Data persistence |
| **Task Queue** | Celery 5.3+ | Distributed task execution |
| **Message Broker** | Redis 7.0+ | Task queue backend, caching |
| **LLM Client** | Custom (Ollama SDK, OpenAI SDK) | LLM integration |
| **Validation** | Pydantic 2.0+ | Data validation |
| **Testing** | pytest 7.4+ | Unit and integration tests |
| **Linting** | Ruff, Black, MyPy | Code quality |
| **Security** | Bandit, Safety | Security scanning |

### Client (Ubuntu)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Instrumentation** | strace, ltrace, perf, GDB | System-level tracing |
| **Sandboxing** | Docker, systemd-nspawn | Isolation |
| **Protocol Libraries** | aiocoap, pymodbus, paho-mqtt, requests | Protocol implementations |
| **Async** | asyncio | Asynchronous execution |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker 24.0+, Docker Compose | Service orchestration |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Prometheus, Grafana (optional) | Metrics and visualization |
| **Load Balancing** | Nginx (optional) | Request distribution |

## Design Principles

### 1. Separation of Concerns

Each component has a single, well-defined responsibility:
- **Server**: Campaign orchestration and intelligence
- **Client**: Payload execution and instrumentation
- **Coordinator**: Integration and result aggregation

### 2. Dependency Inversion

High-level modules depend on abstractions, not concretions:
- Protocol handlers implement `BaseProtocol` interface
- Defense modules implement `BaseDefenseModule` interface
- LLM clients implement unified interface

### 3. Open/Closed Principle

System is open for extension, closed for modification:
- New protocols via protocol registry
- New defense modules via defense integrator
- New LLM providers via client abstraction

### 4. Single Responsibility

Each class/module has one reason to change:
- `PayloadGenerator`: Only payload generation logic
- `DefenseIntegrator`: Only defense coordination
- `LLMJudge`: Only quality assessment

### 5. Interface Segregation

Clients depend only on methods they use:
- Minimal protocol interface
- Separate read/write APIs
- Optional features via mixins

## Scalability

### Horizontal Scaling

**Client Scaling**:
```bash
# Add more execution clients
for i in {1..10}; do
    docker run -d hyfuzz-client --server-url http://server:8080 --client-id client-$i
done
```

**Worker Scaling**:
```bash
# Increase Celery workers
celery -A hyfuzz_server.tasks worker --concurrency=16
```

**Load Balancing**:
```nginx
upstream hyfuzz_backend {
    least_conn;
    server server1:8080;
    server server2:8080;
    server server3:8080;
}
```

### Vertical Scaling

- Increase worker concurrency
- Allocate more CPU/RAM to containers
- Use faster storage (SSD/NVMe)
- Optimize database queries

### Performance Optimization

1. **Caching**: Redis for frequently accessed data
2. **Connection Pooling**: Database and HTTP connections
3. **Batch Processing**: Aggregate multiple operations
4. **Asynchronous I/O**: Non-blocking execution where possible

## Security Architecture

### Defense in Depth

1. **Network Layer**:
   - Firewall rules (UFW/iptables)
   - VPN for cross-host communication
   - TLS/SSL for all HTTP traffic

2. **Application Layer**:
   - API key authentication
   - JWT tokens for session management
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy parameterization)

3. **Execution Layer**:
   - Sandbox isolation (Docker)
   - Resource limits (cgroups)
   - Capability dropping
   - Read-only filesystems where possible

### Threat Model

**Threats**:
- Malicious payloads escaping sandbox
- Unauthorized API access
- Data exfiltration
- Denial of service

**Mitigations**:
- Mandatory sandboxing
- API authentication and rate limiting
- Encrypted data at rest
- Resource quotas

## Extension Points

### Adding a New Protocol

1. **Create protocol handler** (`HyFuzz-Windows-Server/src/protocols/my_protocol.py`):
```python
from .base_protocol import BaseProtocol

class MyProtocol(BaseProtocol):
    def validate(self, payload: dict) -> bool:
        # Validation logic
        pass

    def prepare_request(self, context, payload: dict) -> dict:
        # Request preparation
        pass
```

2. **Register protocol** (in protocol registry):
```python
registry.register("myprotocol", MyProtocol)
```

3. **Implement client executor** (`HyFuzz-Ubuntu-Client/src/protocols/my_protocol.py`)

### Adding a Defense Module

1. **Create defense module** (`HyFuzz-Windows-Server/src/defense/my_defense.py`):
```python
from .defense_integrator import BaseDefenseModule

class MyDefenseModule(BaseDefenseModule):
    def handle_signal(self, signal: DefenseSignal) -> Optional[DefenseResult]:
        # Defense logic
        pass
```

2. **Register module**:
```python
defense_integrator.register_integrator("my_defense", MyDefenseModule())
```

### Adding an LLM Provider

1. **Implement client** (`HyFuzz-Windows-Server/src/llm/my_llm_client.py`):
```python
class MyLLMClient:
    def generate(self, prompt: str, **kwargs) -> str:
        # Generation logic
        pass
```

2. **Update configuration** to support new provider

---

For implementation details, see component-specific documentation:
- [Server Documentation](HyFuzz-Windows-Server/README.md)
- [Client Documentation](HyFuzz-Ubuntu-Client/README.md)
- [Coordinator Documentation](coordinator/README.md)

---

**Last Updated**: 2024-01-01
**Version**: 1.0.0
**Maintainers**: HyFuzz Development Team
