# HyFuzz Quick Start Guide

Get up and running with HyFuzz in 15 minutes.

## Prerequisites

- **Python 3.10+** installed on both Windows and Ubuntu systems
- **Ollama** or OpenAI API access for LLM functionality
- **Git** for repository cloning

## 🚀 Quick Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Install Windows Server dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt

# Install Ubuntu Client dependencies
cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt

# Install testing dependencies (optional)
cd ..
pip install pytest pytest-asyncio
```

### 2. Configure Environment

```bash
# Copy environment templates
cp HyFuzz-Windows-Server/.env.example HyFuzz-Windows-Server/.env
cp HyFuzz-Ubuntu-Client/.env.example HyFuzz-Ubuntu-Client/.env

# Edit .env files with your settings
# At minimum, configure:
# - OLLAMA_ENDPOINT (e.g., http://localhost:11434)
# - DATABASE_URL (default SQLite works out of the box)
```

### 3. Run Health Check

```bash
# Verify your installation
python scripts/health_check.py --verbose
```

Expected output:
```
✓ Windows Server: Server components available
✓ Ubuntu Client: Client components available
✓ Database: Data directory accessible
✓ Dependencies: All required packages installed
✓ Configuration: Configuration files present
```

## 🎯 Running Your First Campaign

### Option A: Using the Phase 3 Coordinator

```bash
# Run the demo test suite
pytest tests/test_phase3_coordinator.py -v

# Or use the coordinator directly
python -m phase3.coordinator \
    --protocol coap \
    --plan configs/phase3_demo.yaml
```

### Option B: Using the Campaign Runner

```bash
# Run a simple CoAP fuzzing campaign
cd HyFuzz-Windows-Server
python scripts/run_fuzzing_campaign.py \
    --name my-first-campaign \
    --protocol coap \
    --target coap://localhost:5683 \
    --payloads 10 \
    --dry-run  # Remove --dry-run for actual execution
```

### Option C: Start the Full Stack

```bash
# Terminal 1: Start Windows Server
cd HyFuzz-Windows-Server
python scripts/start_server.py

# Terminal 2: Start Workers (optional)
cd HyFuzz-Windows-Server
python scripts/start_workers.py --concurrency 4

# Terminal 3: Start Dashboard (optional)
cd HyFuzz-Windows-Server
python scripts/start_dashboard.py

# Terminal 4: Start Ubuntu Client
cd HyFuzz-Ubuntu-Client
python scripts/start_client.py
```

Then visit `http://localhost:8888` to view the monitoring dashboard.

## 📊 Understanding Results

Campaign results are saved in `results/<protocol>/<campaign_name>_<timestamp>.json`

```bash
# View latest campaign results
cat results/coap/my-first-campaign_*.json | jq '.statistics'
```

Example output:
```json
{
  "total_executions": 10,
  "successful_executions": 10,
  "success_rate": 1.0,
  "defense_verdicts": {
    "monitor": 5,
    "investigate": 3,
    "block": 2
  },
  "average_judge_score": 0.65,
  "average_execution_time_ms": 12.5
}
```

## 🔧 Common Tasks

### Generate Custom Payloads

```python
from phase3 import Phase3Coordinator, CampaignTarget

coordinator = Phase3Coordinator(model_name="mistral")
targets = [
    CampaignTarget(
        name="my-coap-server",
        protocol="coap",
        endpoint="coap://192.168.1.100:5683"
    )
]

result = coordinator.run_campaign(targets)
print(result.summary)
```

### Monitor Campaign Progress

```bash
# Watch campaign logs in real-time
tail -f HyFuzz-Windows-Server/logs/campaigns/*.log

# Check defense verdicts
grep -i "verdict" HyFuzz-Windows-Server/logs/campaigns/*.log
```

### Test Protocol Support

```bash
# Test CoAP
cd HyFuzz-Ubuntu-Client
python scripts/run_coap_test.py

# Test Modbus
python scripts/run_modbus_test.py

# Test MQTT
python scripts/run_mqtt_test.py
```

## ⚙️ Configuration Customization

### Edit Campaign Settings

Edit `configs/phase3_demo.yaml`:

```yaml
campaign:
  name: "my-custom-campaign"

fuzzing:
  generation:
    model: "mistral"
    max_samples: 50
    creativity: 0.8

  defense:
    enabled: true
    thresholds:
      block_score: 0.9
      investigate_score: 0.6
```

### Enable Defense Modules

Edit `HyFuzz-Windows-Server/.env`:

```bash
DEFENSE_ENABLED=true
DEFENSE_MODULES=signature_detector,anomaly_detector,behavior_analyzer
DEFENSE_BLOCK_THRESHOLD=0.8
```

### Configure LLM Models

```bash
# Use Ollama (local)
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=mistral

# Or use OpenAI API
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pydantic'"

```bash
pip install -r HyFuzz-Windows-Server/requirements.txt
pip install -r HyFuzz-Ubuntu-Client/requirements.txt
```

### "Connection refused" when starting server

Check if the port is already in use:

```bash
# Linux/Mac
lsof -i :8080

# Windows
netstat -ano | findstr :8080
```

### Dashboard not loading

```bash
# Install dashboard dependencies
pip install fastapi uvicorn
# Or
pip install -r HyFuzz-Windows-Server/requirements-dev.txt
```

### LLM endpoint not responding

```bash
# Test Ollama connectivity
curl http://localhost:11434/api/version

# If Ollama isn't running, start it:
ollama serve

# Download a model if needed:
ollama pull mistral
```

## 📚 Next Steps

- Read the [Full Documentation](README.md)
- Explore [Protocol Integration Guide](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md)
- Set up [Defense Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md)
- Configure [Instrumentation](HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md)
- Review [Testing Strategy](tests/README.md)

## 💡 Tips

1. **Start Small**: Begin with 10-20 payloads to validate your setup
2. **Use Dry Run**: Test campaigns with `--dry-run` first
3. **Monitor Resources**: Watch CPU/memory usage during campaigns
4. **Check Logs**: Logs are your friend - check them first when debugging
5. **Incremental Testing**: Test one protocol at a time initially

## 🆘 Getting Help

- **GitHub Issues**: https://github.com/your-org/HyFuzz/issues
- **Documentation**: See `docs/` directories in each component
- **Health Check**: Run `python scripts/health_check.py -v` for diagnostics

## ✅ Checklist

After following this guide, you should have:

- [ ] Installed all dependencies
- [ ] Configured environment variables
- [ ] Run health check successfully
- [ ] Executed a test campaign
- [ ] Viewed results in `results/` directory
- [ ] (Optional) Started the monitoring dashboard
- [ ] (Optional) Run the full test suite

---

**Ready to fuzz?** Start with the demo campaign:

```bash
python -m phase3.coordinator --protocol coap --plan configs/phase3_demo.yaml
```

Happy fuzzing! 🎯
