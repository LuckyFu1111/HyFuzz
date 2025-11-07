# HyFuzz Quick Start Guide

Get HyFuzz up and running in 5 minutes!

## 📋 Prerequisites

- **Python 3.9+** installed on all machines
- **Ollama** installed on server machines (for LLM support)
- Network connectivity between server and clients

## 🚀 Quick Start

### Option 1: Windows Server + Ubuntu Client (Recommended)

#### Step 1: Start Windows Server

```powershell
# On Windows machine
cd HyFuzz-Windows-Server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m src
```

Server starts at: `http://0.0.0.0:8080`

#### Step 2: Start Ubuntu Client

```bash
# On Ubuntu machine
cd HyFuzz-Ubuntu-Client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MCP_SERVER_HOST=<WINDOWS_SERVER_IP>
python -m src
```

### Option 2: macOS Server + Ubuntu Client

#### Step 1: Start macOS Server

```bash
# On macOS machine
cd HyFuzz-Mac-Server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: Run performance optimization
python scripts/optimize_macos.py

# Start server
./scripts/start_server.sh
# Or manually:
python -m src
```

Server starts at: `http://0.0.0.0:8080`

#### Step 2: Start Ubuntu Client

```bash
# On Ubuntu machine
cd HyFuzz-Ubuntu-Client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MCP_SERVER_HOST=<MACOS_SERVER_IP>
python -m src
```

## 🔧 Configuration

### Server Configuration

Edit `.env` file (copy from `.env.example`):

```bash
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
DATABASE_URL=sqlite:///data/hyfuzz.db
OLLAMA_ENDPOINT=http://localhost:11434
LOG_LEVEL=INFO
```

### Client Configuration

Set environment variables:

```bash
export MCP_SERVER_HOST=<SERVER_IP>
export MCP_SERVER_PORT=8080
export LOG_LEVEL=INFO
```

## ✅ Verify Installation

### Check Server Health

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Check Client Connection

```bash
# From client machine
curl http://<SERVER_IP>:8080/health
```

## 🎯 First Fuzzing Campaign

### Using the GUI (Windows/Mac Server)

1. Start the GUI:
   ```bash
   cd ui
   python launch_gui.py
   ```

2. Create a new campaign:
   - Campaign name: `my-first-test`
   - Protocol: `coap`
   - Target: `localhost:5683`
   - Payload count: `10`

3. Start the campaign and monitor progress

### Using the API

```bash
# Create campaign
curl -X POST http://localhost:8080/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-first-test",
    "protocol": "coap",
    "target": "localhost:5683",
    "payload_count": 10
  }'

# Start campaign
curl -X POST http://localhost:8080/api/campaigns/<campaign_id>/start

# Check status
curl http://localhost:8080/api/campaigns/<campaign_id>/status
```

## 📊 Supported Protocols

| Protocol | Default Port | Example Target |
|----------|-------------|----------------|
| CoAP | 5683 | `localhost:5683` |
| Modbus | 502 | `localhost:502` |
| MQTT | 1883 | `localhost:1883` |
| HTTP | 80/443 | `http://localhost:8000` |
| gRPC | 50051 | `localhost:50051` |
| JSON-RPC | 8545 | `localhost:8545` |

## 🐛 Common Issues

### Server won't start

**Problem**: Port 8080 already in use
```bash
# Solution: Change port in .env
MCP_SERVER_PORT=8081
```

**Problem**: Ollama not running
```bash
# Solution: Start Ollama
ollama serve
```

### Client can't connect

**Problem**: Firewall blocking connection
```bash
# Solution: Allow port 8080 through firewall
# Windows:
netsh advfirewall firewall add rule name="HyFuzz" dir=in action=allow protocol=TCP localport=8080

# Ubuntu:
sudo ufw allow 8080/tcp

# macOS:
# System Preferences → Security & Privacy → Firewall → Firewall Options
```

**Problem**: Wrong server IP
```bash
# Solution: Check server IP
# Windows:
ipconfig

# Linux/macOS:
ifconfig
# or
ip addr show
```

### Performance issues on macOS

```bash
# Run optimization script
cd HyFuzz-Mac-Server
python scripts/optimize_macos.py

# Monitor performance
python scripts/monitor_performance_macos.py
```

## 📖 Next Steps

- **Detailed Setup**: See component-specific README files
  - [Windows Server Setup](HyFuzz-Windows-Server/SETUP_GUIDE.md)
  - [macOS Server Setup](HyFuzz-Mac-Server/README.md)
  - [Ubuntu Client Setup](HyFuzz-Ubuntu-Client/docs/SETUP.md)

- **Architecture**: Read [ARCHITECTURE.md](HyFuzz-Windows-Server/docs/ARCHITECTURE.md)
- **API Documentation**: See [API.md](HyFuzz-Windows-Server/docs/API.md)
- **Deployment**: Read [DEPLOYMENT.md](HyFuzz-Windows-Server/docs/DEPLOYMENT.md)

## 🆘 Getting Help

- **Documentation**: See `/docs` in each component directory
- **GUI Help**: Press F1 in the GUI
- **Issues**: https://github.com/LuckyFu1111/HyFuzz/issues

## 🚦 System Requirements

### Windows Server
- Windows 10/11 or Windows Server 2019+
- 8GB+ RAM recommended
- Python 3.9+
- Ollama

### macOS Server
- macOS 12 (Monterey) or later
- 8GB+ RAM (16GB+ recommended for Apple Silicon)
- Python 3.9+
- Ollama with Metal support

### Ubuntu Client
- Ubuntu 20.04 LTS or later
- 4GB+ RAM recommended
- Python 3.9+
- System tools: `strace`, `ltrace`, `gdb`

---

**Happy Fuzzing! 🚀**
