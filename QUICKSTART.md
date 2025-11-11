# HyFuzz Quick Start Guide

Get HyFuzz up and running in 5 minutes! This guide will help you set up and run your first fuzzing campaign.

> **Note**: This is a quick start guide for getting HyFuzz running quickly. For detailed installation and configuration, see the component-specific documentation.

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

## 🐛 Common Issues & Solutions

### Server Issues

#### Server won't start

**Problem**: Port 8080 already in use
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :8080

# Linux/macOS:
lsof -i :8080

# Solution: Change port in .env
MCP_SERVER_PORT=8081
```

**Problem**: Ollama not running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Solution: Start Ollama
ollama serve

# Pull required model if not present
ollama pull llama2
```

**Problem**: Database initialization failed
```bash
# Solution: Initialize database manually
cd HyFuzz-Windows-Server  # or HyFuzz-Mac-Server
python scripts/init_db.py

# Reset database if corrupted
python scripts/reset_db.py --confirm
```

**Problem**: Missing dependencies
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# For development dependencies
pip install -r requirements-dev.txt
```

### Client Issues

#### Client can't connect to server

**Problem**: Firewall blocking connection
```bash
# Solution: Allow port 8080 through firewall

# Windows:
netsh advfirewall firewall add rule name="HyFuzz" dir=in action=allow protocol=TCP localport=8080

# Ubuntu:
sudo ufw allow 8080/tcp
sudo ufw reload

# macOS:
# System Preferences → Security & Privacy → Firewall → Firewall Options
# Add Python to allowed apps
```

**Problem**: Wrong server IP
```bash
# Solution: Find correct server IP

# Windows:
ipconfig
# Look for IPv4 Address

# Linux:
ip addr show
# or
hostname -I

# macOS:
ifconfig en0 | grep inet
```

**Problem**: Network latency issues
```bash
# Test connection quality
ping <SERVER_IP>

# Test port connectivity
telnet <SERVER_IP> 8080
# or
nc -zv <SERVER_IP> 8080
```

#### Client execution errors

**Problem**: Permission denied errors
```bash
# Solution: Ensure proper permissions
sudo usermod -aG docker $USER
# Logout and login again

# For specific tools
sudo chmod +x /usr/bin/strace
```

**Problem**: Sandbox creation fails
```bash
# Solution: Check system requirements
# Install required packages
sudo apt-get update
sudo apt-get install -y cgroup-tools libseccomp-dev

# Verify cgroups
mount | grep cgroup
```

### Performance Issues

#### Slow payload generation (Server)

**Problem**: LLM inference is slow
```bash
# Solution: Check Ollama performance
ollama ps

# Try a smaller model
ollama pull llama2:7b  # Instead of 13b or 70b

# macOS: Run optimization
cd HyFuzz-Mac-Server
python scripts/optimize_macos.py
```

**Problem**: High memory usage
```bash
# Solution: Adjust configuration
# In .env file:
MAX_CONCURRENT_CAMPAIGNS=2
LLM_BATCH_SIZE=1
CACHE_SIZE=100

# Monitor memory
# Windows: Task Manager
# Linux: htop or top
# macOS: Activity Monitor
```

#### Slow payload execution (Client)

**Problem**: Instrumentation overhead
```bash
# Solution: Disable unnecessary instrumentation
# In client config:
ENABLE_STRACE=false
ENABLE_LTRACE=false
ENABLE_COVERAGE=true  # Keep only essential

# Use lighter sandbox
SANDBOX_MODE=minimal
```

**Problem**: Too many parallel executions
```bash
# Solution: Reduce worker count
export MAX_WORKERS=2  # Instead of auto-detected

# Check system load
uptime
```

### Protocol-Specific Issues

#### CoAP fuzzing issues

**Problem**: CoAP server not responding
```bash
# Solution: Start CoAP test server
cd examples/targets/coap
python coap_server.py

# Test manually
coap-client -m get coap://localhost:5683/
```

#### Modbus fuzzing issues

**Problem**: Modbus connection refused
```bash
# Solution: Check Modbus server
# Install modbus simulator
pip install pymodbus

# Start test server
python examples/targets/modbus/modbus_server.py

# Test connection
python examples/targets/modbus/test_connection.py
```

### Dashboard Issues

**Problem**: Dashboard won't load
```bash
# Solution: Check web server logs
tail -f logs/dashboard.log

# Clear browser cache
# Chrome: Ctrl+Shift+Del
# Firefox: Ctrl+Shift+Del

# Rebuild static assets
cd ui/
npm install
npm run build
```

**Problem**: Real-time updates not working
```bash
# Solution: Check WebSocket connection
# Open browser console (F12)
# Look for WebSocket errors

# Restart server with WebSocket logging
export WS_DEBUG=true
python -m src
```

### General Troubleshooting

**Problem**: Logs are not helpful enough
```bash
# Solution: Enable debug logging
export LOG_LEVEL=DEBUG

# For specific modules
export LLM_LOG_LEVEL=DEBUG
export MCP_LOG_LEVEL=DEBUG

# Check log files
tail -f logs/hyfuzz.log
```

**Problem**: Configuration not taking effect
```bash
# Solution: Check config precedence
# Order: CLI args > Environment vars > .env file > defaults

# Verify current config
python scripts/show_config.py

# Validate config file
python scripts/validate_config.py
```

**Problem**: Dependencies conflict
```bash
# Solution: Use clean virtual environment
# Remove old environment
rm -rf venv/

# Create fresh environment
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Verify installation
pip check
```

## 🧪 Testing Your Setup

### End-to-End Test

After starting both server and client, verify the complete setup:

```bash
# Check server is accepting connections
curl http://localhost:8080/health

# Check server can reach Ollama
curl http://localhost:8080/api/llm/status

# List connected clients
curl http://localhost:8080/api/clients

# Run a quick test campaign
curl -X POST http://localhost:8080/api/campaigns/test \
  -H "Content-Type: application/json" \
  -d '{"protocol": "coap", "target": "localhost:5683", "count": 5}'
```

### Expected Results

After running a test campaign, you should see:

1. **Server logs**: Payload generation messages
2. **Client logs**: Execution and result reporting
3. **Dashboard**: Campaign appears with status updates
4. **Results**: Payloads executed and results collected

## 📊 Understanding Results

### Result Structure

Each campaign produces:

```
results/
├── campaign_<id>/
│   ├── payloads/          # Generated payloads
│   ├── executions/        # Execution logs
│   ├── crashes/           # Crash reports (if any)
│   ├── coverage/          # Coverage data
│   └── report.html        # Summary report
```

### Viewing Reports

```bash
# Open HTML report in browser
open results/campaign_<id>/report.html

# View crash summary
cat results/campaign_<id>/crashes/summary.txt

# Check coverage
python scripts/coverage_report.py results/campaign_<id>/
```

## 📖 Next Steps

### Essential Reading

1. **Component Setup Guides**:
   - [Windows Server Setup](HyFuzz-Windows-Server/SETUP_GUIDE.md)
   - [macOS Server Setup](HyFuzz-Mac-Server/README.md)
   - [Ubuntu Client Setup](HyFuzz-Ubuntu-Client/docs/SETUP.md)

2. **Architecture & Design**:
   - [System Architecture](HyFuzz-Windows-Server/docs/ARCHITECTURE.md)
   - [Protocol Guide](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md)
   - [LLM Integration](HyFuzz-Windows-Server/docs/LLM_INTEGRATION.md)

3. **Usage Guides**:
   - [API Documentation](HyFuzz-Windows-Server/docs/API.md)
   - [Campaign Management](HyFuzz-Windows-Server/docs/CAMPAIGNS.md)
   - [Result Analysis](HyFuzz-Windows-Server/docs/ANALYSIS.md)

4. **Advanced Topics**:
   - [Deployment Guide](HyFuzz-Windows-Server/docs/DEPLOYMENT.md)
   - [Performance Tuning](HyFuzz-Mac-Server/docs/MACOS_PERFORMANCE.md)
   - [Defense Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md)

### Learn by Example

Check out example campaigns in:
- `examples/campaigns/` - Sample campaign configurations
- `examples/targets/` - Test target implementations
- `examples/results/` - Example result analysis

### Join the Community

- **Questions**: [GitHub Discussions](https://github.com/LuckyFu1111/HyFuzz/discussions)
- **Issues**: [Bug Reports](https://github.com/LuckyFu1111/HyFuzz/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

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
