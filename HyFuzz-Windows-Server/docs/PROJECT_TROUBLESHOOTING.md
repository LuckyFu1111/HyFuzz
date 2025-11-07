# HyFuzz Troubleshooting Guide

This guide helps you diagnose and fix common issues with HyFuzz.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [Configuration Issues](#configuration-issues)
- [Docker Issues](#docker-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Debug Mode](#debug-mode)
- [Getting Help](#getting-help)

## Quick Diagnostics

Start with these commands to identify issues:

```bash
# 1. Run health check
python scripts/health_check.py --verbose

# 2. Verify Python version (requires 3.10+)
python3 --version

# 3. Check installed packages
pip list | grep -E "pydantic|pytest|requests|aiohttp"

# 4. Run integration tests
pytest tests/test_integration.py -v

# 5. Verify database
python scripts/init_database.py --verify
```

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'pydantic'`

**Cause**: Missing Python dependencies

**Solution**:
```bash
# Install all dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt

cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt

# Or use Make
make install
```

### Issue: `ImportError: cannot import name 'FuzzingCoordinator'`

**Cause**: Python path not configured correctly

**Solution**:
```bash
# Ensure you're in the project root
cd /path/to/HyFuzz

# Verify coordinator package
python3 -c "from coordinator import FuzzingCoordinator; print('OK')"

# If still failing, check PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Issue: `pip install` fails with "permission denied"

**Solutions**:
```bash
# Option 1: Use --user flag
pip install --user -r requirements.txt

# Option 2: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 3: Use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Issue: Python 3.13 compatibility issues

**Cause**: Some packages may not yet support Python 3.13

**Solution**:
```bash
# Use Python 3.11 or 3.12
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Runtime Issues

### Issue: `start_server.py` fails with "Address already in use"

**Cause**: Port 8080 is already occupied

**Solution**:
```bash
# Option 1: Find and kill the process
lsof -i :8080  # Linux/Mac
netstat -ano | findstr :8080  # Windows

# Option 2: Use a different port
python scripts/start_server.py --port 8081

# Option 3: Edit .env file
echo "MCP_SERVER_PORT=8081" >> .env
```

### Issue: Database initialization fails

**Symptoms**:
```
ERROR - Database initialization failed
sqlite3.OperationalError: unable to open database file
```

**Solutions**:
```bash
# 1. Check directory permissions
mkdir -p data
chmod 755 data

# 2. Verify database path
python scripts/init_database.py --database-url sqlite:///$(pwd)/data/hyfuzz.db

# 3. Use absolute path
python scripts/init_database.py --database-url sqlite:////absolute/path/to/data/hyfuzz.db
```

### Issue: "Connection refused" when accessing server

**Diagnosis**:
```bash
# Check if server is running
ps aux | grep start_server.py

# Check if port is listening
netstat -tuln | grep 8080

# Check firewall
sudo ufw status  # Linux
```

**Solutions**:
```bash
# 1. Start server with host 0.0.0.0
python scripts/start_server.py --host 0.0.0.0

# 2. Check firewall rules
sudo ufw allow 8080/tcp

# 3. Verify server logs
tail -f logs/server.log
```

### Issue: Dashboard not loading

**Symptoms**: HTTP 500 error or connection timeout

**Solutions**:
```bash
# 1. Install dashboard dependencies
pip install fastapi uvicorn

# 2. Start dashboard separately
python scripts/start_dashboard.py --port 8888

# 3. Check if FastAPI is available
python3 -c "import fastapi; print(fastapi.__version__)"

# 4. View dashboard logs
tail -f logs/dashboard.log
```

## Configuration Issues

### Issue: Ollama endpoint not reachable

**Symptoms**:
```
WARNING - Failed to connect to Ollama: Connection refused
```

**Solutions**:
```bash
# 1. Check if Ollama is running
curl http://localhost:11434/api/version

# 2. Start Ollama
ollama serve

# 3. Update .env with correct endpoint
echo "OLLAMA_ENDPOINT=http://localhost:11434" >> .env

# 4. Use OpenAI instead
echo "OPENAI_API_KEY=your-key" >> .env
```

### Issue: `.env` file not being read

**Cause**: File in wrong location or incorrect format

**Solutions**:
```bash
# 1. Verify .env location
ls -la HyFuzz-Windows-Server/.env
ls -la HyFuzz-Ubuntu-Client/.env

# 2. Check file format (no spaces around =)
# Correct:   KEY=value
# Incorrect: KEY = value

# 3. Reload environment
source .env  # If using bash

# 4. Debug with
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OLLAMA_ENDPOINT'))"
```

### Issue: YAML configuration errors

**Symptoms**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solutions**:
```bash
# 1. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('configs/campaign_demo.yaml'))"

# 2. Check indentation (use spaces, not tabs)
# 3. Escape special characters with quotes
# 4. Use YAML validator online
```

## Docker Issues

### Issue: `docker-compose up` fails

**Common causes and solutions**:

#### "Cannot connect to Docker daemon"
```bash
# Start Docker daemon
sudo systemctl start docker

# Or on Windows/Mac, start Docker Desktop
```

#### "Port is already allocated"
```bash
# Stop conflicting containers
docker-compose down

# Or use different ports in docker-compose.yml
```

#### "No space left on device"
```bash
# Clean up Docker resources
docker system prune -a --volumes

# Check disk space
df -h
```

### Issue: Container keeps restarting

**Diagnosis**:
```bash
# View container logs
docker-compose logs -f server

# Check container status
docker-compose ps

# Inspect specific container
docker inspect hyfuzz-server
```

**Solutions**:
```bash
# 1. Fix configuration errors in .env
# 2. Ensure volumes have correct permissions
# 3. Check resource limits
docker stats
```

### Issue: Containers can't communicate

**Symptoms**: "Connection refused" between services

**Solutions**:
```bash
# 1. Verify network
docker network ls
docker network inspect hyfuzz-network

# 2. Use service names (not localhost)
# Correct:   http://server:8080
# Incorrect: http://localhost:8080

# 3. Restart Docker network
docker-compose down
docker-compose up -d
```

## Performance Issues

### Issue: Slow payload generation

**Causes**:
- LLM model too large
- Insufficient CPU/RAM
- Network latency to LLM service

**Solutions**:
```bash
# 1. Use smaller model
ollama pull mistral:7b  # Instead of larger models

# 2. Reduce payload count
python scripts/run_fuzzing_campaign.py --payloads 10  # Instead of 100

# 3. Monitor resource usage
htop
docker stats

# 4. Increase worker concurrency
python scripts/start_workers.py --concurrency 8
```

### Issue: High memory usage

**Solutions**:
```bash
# 1. Limit concurrent campaigns
# Edit .env: MAX_CONCURRENT_CAMPAIGNS=2

# 2. Reduce cache size
# Edit .env: CACHE_MAX_SIZE=500

# 3. Clear old results
make clean-all

# 4. Monitor memory
watch -n 1 'ps aux | grep python | awk "{sum+=\$4} END {print sum}"'
```

### Issue: Database growing too large

**Solutions**:
```bash
# 1. Clean old campaigns
sqlite3 data/hyfuzz.db "DELETE FROM campaigns WHERE created_at < date('now', '-30 days');"

# 2. Vacuum database
sqlite3 data/hyfuzz.db "VACUUM;"

# 3. Archive old data
sqlite3 data/hyfuzz.db ".backup data/hyfuzz_backup_$(date +%Y%m%d).db"

# 4. Use PostgreSQL for better performance
```

## Common Error Messages

### `WARNING - Utility components import failed: cannot import name 'CustomException'`

**Impact**: Low - This is expected in mock mode

**Solution**: Not required for basic functionality. Ignore if health check passes.

### `ModuleNotFoundError: No module named 'websockets'`

**Solution**:
```bash
pip install websockets
# Or install all dev dependencies
pip install -r requirements-dev.txt
```

### `FileNotFoundError: [Errno 2] No such file or directory: 'config/server_config.yaml'`

**Solution**:
```bash
# Ensure you're in the correct directory
cd HyFuzz-Windows-Server

# Verify config exists
ls -la config/server_config.yaml

# Or use absolute path
python scripts/start_server.py --config /absolute/path/to/server_config.yaml
```

### `RuntimeError: This event loop is already running`

**Cause**: Async conflict, often in Jupyter notebooks

**Solution**:
```python
# Use nest_asyncio for Jupyter
import nest_asyncio
nest_asyncio.apply()

# Or run in regular Python script instead
```

### `sqlite3.OperationalError: database is locked`

**Cause**: Multiple processes accessing SQLite

**Solutions**:
```bash
# 1. Close other connections
lsof data/hyfuzz.db

# 2. Use PostgreSQL for concurrent access
# Edit docker-compose.yml and use postgres service

# 3. Increase timeout
# Edit: DATABASE_URL=sqlite:///data/hyfuzz.db?timeout=30
```

## Debug Mode

Enable detailed logging for troubleshooting:

### Server Debug Mode
```bash
# Via command line
python scripts/start_server.py --log-level DEBUG

# Via .env
echo "LOG_LEVEL=DEBUG" >> .env

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Client Debug Mode
```bash
# Via command line
python scripts/start_client.py --log-level DEBUG

# Via .env
echo "LOG_LEVEL=DEBUG" >> .env
```

### View detailed logs
```bash
# Follow server logs
tail -f logs/server.log

# Follow campaign logs
tail -f logs/campaigns/*.log

# View all logs
find logs/ -name "*.log" -exec tail -f {} +

# Filter for errors
grep -r "ERROR" logs/

# Filter for specific component
grep -r "Defense" logs/
```

### Profiling Performance
```bash
# CPU profiling
python -m cProfile -o profile.stats scripts/run_fuzzing_campaign.py

# Memory profiling
mprof run scripts/run_fuzzing_campaign.py
mprof plot

# Line profiling
kernprof -l -v scripts/run_fuzzing_campaign.py
```

## Testing Issues

### Issue: Tests fail with import errors

**Solution**:
```bash
# Ensure pytest can find modules
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run from project root
cd /path/to/HyFuzz
pytest tests/
```

### Issue: Async tests timing out

**Solution**:
```bash
# Increase timeout
pytest tests/ --timeout=300

# Or mark test with longer timeout
@pytest.mark.asyncio
@pytest.mark.timeout(600)
async def test_long_running():
    pass
```

## Getting Help

### Self-Service Diagnostics

1. **Run comprehensive checks**:
   ```bash
   make ci  # Run all quality checks
   python scripts/health_check.py --verbose --json > diagnostics.json
   ```

2. **Collect system information**:
   ```bash
   python3 --version
   pip list > installed_packages.txt
   docker --version
   cat /etc/os-release  # Linux
   ```

3. **Check logs**:
   ```bash
   # Compress logs for sharing
   tar -czf hyfuzz_logs.tar.gz logs/
   ```

### Reporting Issues

When asking for help, include:

1. **Environment**:
   - OS and version
   - Python version
   - HyFuzz version/commit
   - Installation method (pip, docker, source)

2. **What you tried**:
   - Exact command that failed
   - Error message (full stack trace)
   - Configuration (sanitized .env)

3. **Diagnostics**:
   - Output of `python scripts/health_check.py --verbose`
   - Relevant log files
   - Output of `pip list`

4. **Minimal reproduction**:
   - Simplest steps to reproduce
   - Sample configuration/code

### Community Support

- **GitHub Issues**: https://github.com/your-org/HyFuzz/issues
- **Discussions**: https://github.com/your-org/HyFuzz/discussions
- **Documentation**: Check all docs in `docs/` directories

### Professional Support

For enterprise support, contact: support@hyfuzz.example.com

---

## Appendix: Health Check Interpretation

```bash
python scripts/health_check.py --verbose
```

**Output interpretation**:

- ✓ **Healthy**: Component working correctly
- ⚠ **Degraded**: Component working but with warnings
- ✗ **Unhealthy**: Component not working, immediate action required
- ? **Unknown**: Cannot determine status

**Components checked**:
1. Windows Server - Core server availability
2. Ubuntu Client - Client components
3. Database - Database accessibility and permissions
4. Dependencies - Required Python packages
5. Configuration - Configuration file presence

**Next steps by status**:
- All Healthy → Proceed with usage
- Some Degraded → Review warnings, may work with limitations
- Any Unhealthy → Fix issues before proceeding
- Unknown → Check logs and permissions

---

**Remember**: Most issues can be solved by:
1. Checking you're in the right directory
2. Ensuring dependencies are installed
3. Verifying configuration files exist
4. Reading error messages carefully
5. Checking logs for details

Good luck! 🔧
