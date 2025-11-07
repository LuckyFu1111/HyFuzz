# macOS Performance Optimization Guide

This guide covers macOS-specific performance optimizations for HyFuzz Server, with special focus on Apple Silicon (M1/M2/M3/M4) processors.

## Table of Contents

- [Quick Start](#quick-start)
- [Hardware-Specific Optimizations](#hardware-specific-optimizations)
- [System Configuration](#system-configuration)
- [Ollama Optimization](#ollama-optimization)
- [Performance Monitoring](#performance-monitoring)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Automatic Optimization

Run the automatic optimization script to detect your hardware and apply optimal settings:

```bash
cd HyFuzz-Mac-Server
python3 scripts/optimize_macos.py
```

This will:
- Detect your Mac's hardware (Apple Silicon vs Intel)
- Calculate optimal worker pool size
- Configure memory and cache settings
- Set up Ollama for best performance
- Create LaunchD service configuration

### Manual Performance Check

Monitor real-time performance:

```bash
python3 scripts/monitor_performance_macos.py
```

---

## Hardware-Specific Optimizations

### Apple Silicon (M1/M2/M3/M4)

Apple Silicon Macs offer exceptional performance for LLM workloads due to:

- **Unified Memory Architecture**: Shared memory between CPU and GPU
- **Metal Performance Shaders**: Hardware-accelerated ML operations
- **Neural Engine**: Dedicated ML acceleration
- **Efficient/Performance Core Design**: Optimal task distribution

#### Recommended Settings for Apple Silicon

**For 8GB RAM (M1/M2 Base):**
```yaml
worker_pool_size: 8
cache_size_mb: 1024
llm_batch_size: 4
max_memory_percent: 60
profile: power_saving
```

**For 16GB RAM (M1/M2 Pro, M3):**
```yaml
worker_pool_size: 12
cache_size_mb: 2048
llm_batch_size: 8
max_memory_percent: 70
profile: balanced
```

**For 32GB+ RAM (M1/M2/M3 Max, M3 Ultra):**
```yaml
worker_pool_size: 16
cache_size_mb: 4096
llm_batch_size: 16
max_memory_percent: 75
profile: max_performance
```

#### Ollama on Apple Silicon

Enable Metal acceleration for significant performance gains:

```bash
# Set environment variables
export OLLAMA_USE_METAL=1
export OLLAMA_NUM_PARALLEL=8

# Start Ollama
ollama serve
```

**Model Recommendations:**

| RAM | Recommended Models | Notes |
|-----|-------------------|-------|
| 8GB | mistral (7B), neural-chat (7B) | Quantized versions preferred |
| 16GB | mistral (7B), codellama (13B) | Full precision possible |
| 32GB+ | mixtral (8x7B), llama2 (70B) | Large models with excellent performance |

### Intel Macs

Intel Macs can still run HyFuzz efficiently with appropriate settings:

**Recommended Settings:**
```yaml
worker_pool_size: 8  # Based on logical cores
cache_size_mb: 1024
llm_batch_size: 4
max_memory_percent: 70
use_metal: false
```

**Performance Tips:**
- Use smaller models (3B-7B parameters)
- Enable AVX2 optimizations if available
- Consider quantized models for better performance

---

## System Configuration

### File Descriptor Limits

Increase file descriptor limits for better I/O performance:

```bash
# Check current limits
launchctl limit maxfiles

# Increase limits (requires restart)
sudo launchctl limit maxfiles 65536 200000
```

### Memory Pressure Management

macOS manages memory pressure automatically, but you can optimize:

```bash
# Monitor memory pressure
memory_pressure

# Check swap usage
sysctl vm.swapusage
```

**Optimization Tips:**
- Keep memory pressure in "normal" zone
- If you see "warning" or "critical", reduce `max_memory_percent`
- Close unnecessary applications when running intensive campaigns

### Energy Settings (MacBooks)

For optimal performance on battery:

```bash
# Prevent App Nap
defaults write com.hyfuzz.server NSAppSleepDisabled -bool YES

# Set to high performance mode
sudo pmset -b powermode 1
```

For plugged-in operation:

```bash
# Maximum performance
sudo pmset -c powermode 2
```

---

## Ollama Optimization

### Installation

```bash
# Install via Homebrew (recommended)
brew install ollama

# Verify installation
ollama --version
```

### Configuration

Create Ollama configuration for optimal performance:

```bash
# Source the generated config
source config/ollama_macos.env

# Start Ollama with optimizations
ollama serve
```

### Model Selection and Management

**Pull optimized models:**

```bash
# For Apple Silicon with 16GB+ RAM
ollama pull mistral
ollama pull codellama:13b

# For 8GB RAM
ollama pull mistral:7b-q4
ollama pull neural-chat:7b-q4
```

**Check model performance:**

```bash
# Run benchmark
ollama run mistral "Generate a test payload for XSS vulnerability"
```

### Performance Tuning

Edit `.env` file:

```bash
# LLM Configuration
OLLAMA_API_URL=http://localhost:11434
LLM_MODEL_NAME=mistral
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# Cache settings
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=7200

# Apple Silicon specific
OLLAMA_USE_METAL=1
OLLAMA_NUM_PARALLEL=8
```

---

## Performance Monitoring

### Real-time Monitoring

Use the built-in performance monitor:

```bash
# Continuous monitoring
python3 scripts/monitor_performance_macos.py

# One-time snapshot
python3 scripts/monitor_performance_macos.py --once
```

**Metrics Displayed:**
- CPU usage (user/system/idle)
- Memory usage and pressure
- Disk I/O throughput
- Active HyFuzz processes
- Apple Silicon specific metrics (battery, temperature)

### System Tools

**Activity Monitor:**
```bash
# Open Activity Monitor
open -a "Activity Monitor"
```

**Command-line monitoring:**

```bash
# CPU usage
top -l 1 | head -n 10

# Memory stats
vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);'

# Disk I/O
iostat -d -c 5
```

### Performance Logs

HyFuzz logs performance metrics automatically:

```bash
# View performance logs
tail -f logs/server.log | grep PERF

# Analyze performance trends
grep PERF logs/server.log | python3 scripts/analyze_performance.py
```

---

## Running as a Service (LaunchD)

### Installation

```bash
# Copy plist file
cp com.hyfuzz.server.plist ~/Library/LaunchAgents/

# Load service
launchctl load ~/Library/LaunchAgents/com.hyfuzz.server.plist

# Check status
launchctl list | grep hyfuzz
```

### Management

```bash
# Start service
launchctl start com.hyfuzz.server

# Stop service
launchctl stop com.hyfuzz.server

# Restart service
launchctl stop com.hyfuzz.server && launchctl start com.hyfuzz.server

# Unload service
launchctl unload ~/Library/LaunchAgents/com.hyfuzz.server.plist
```

### Logs

```bash
# View service logs
tail -f logs/server.log
tail -f logs/server.error.log
```

---

## Troubleshooting

### High CPU Usage

**Symptoms:** CPU usage consistently above 80%

**Solutions:**
1. Reduce worker pool size:
   ```yaml
   worker_pool_size: 4
   ```

2. Lower LLM batch size:
   ```yaml
   llm_batch_size: 4
   ```

3. Use a smaller model:
   ```bash
   ollama pull mistral:7b-q4
   ```

### Memory Pressure

**Symptoms:** Memory pressure warning/critical

**Solutions:**
1. Reduce cache size:
   ```yaml
   cache_size_mb: 512
   ```

2. Lower max memory percentage:
   ```yaml
   max_memory_percent: 50
   ```

3. Restart Ollama to free memory:
   ```bash
   pkill ollama
   ollama serve
   ```

### Slow LLM Inference

**Symptoms:** Payload generation takes > 10 seconds

**Solutions:**

**For Apple Silicon:**
1. Verify Metal is enabled:
   ```bash
   echo $OLLAMA_USE_METAL  # Should be 1
   ```

2. Check GPU memory allocation:
   ```bash
   ps aux | grep ollama
   ```

3. Try a different model:
   ```bash
   ollama pull neural-chat:7b
   ```

**For Intel:**
1. Use quantized models:
   ```bash
   ollama pull mistral:7b-q4
   ```

2. Reduce context size:
   ```yaml
   llm_max_tokens: 1024
   ```

### Disk I/O Bottleneck

**Symptoms:** High disk wait time

**Solutions:**
1. Use SSD if available
2. Reduce logging verbosity:
   ```yaml
   log_level: WARNING
   ```

3. Increase cache TTL:
   ```yaml
   cache_ttl_seconds: 7200
   ```

### Battery Drain (MacBooks)

**Symptoms:** Fast battery drain during fuzzing campaigns

**Solutions:**
1. Use power saving profile:
   ```bash
   python3 scripts/optimize_macos.py --profile power_saving
   ```

2. Reduce worker pool:
   ```yaml
   worker_pool_size: 2
   use_efficiency_cores_only: true
   ```

3. Run on AC power for intensive campaigns

---

## Performance Benchmarks

### Apple Silicon Performance

**M1 (8GB RAM):**
- Payloads/minute: ~60-80
- LLM inference: 2-4 seconds
- Memory usage: 60-70%

**M2 Pro (16GB RAM):**
- Payloads/minute: ~100-120
- LLM inference: 1-2 seconds
- Memory usage: 50-60%

**M3 Max (32GB RAM):**
- Payloads/minute: ~150-200
- LLM inference: 0.5-1 seconds
- Memory usage: 40-50%

### Intel Mac Performance

**Intel i7 (16GB RAM):**
- Payloads/minute: ~40-50
- LLM inference: 5-8 seconds
- Memory usage: 70-80%

---

## Best Practices

1. **Run optimization on first install:**
   ```bash
   python3 scripts/optimize_macos.py
   ```

2. **Monitor performance regularly:**
   ```bash
   python3 scripts/monitor_performance_macos.py --once
   ```

3. **Keep Ollama updated:**
   ```bash
   brew upgrade ollama
   ```

4. **Use appropriate profiles:**
   - `max_performance` for production campaigns
   - `balanced` for daily use
   - `power_saving` for MacBooks on battery

5. **Close unnecessary applications** during intensive fuzzing

6. **Regular maintenance:**
   ```bash
   # Clean caches
   rm -rf data/results/*
   rm -rf logs/*.log.old

   # Restart Ollama weekly
   pkill ollama && ollama serve
   ```

---

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Apple Silicon Optimization Guide](https://developer.apple.com/metal/)
- [macOS Performance Guide](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)

---

**Need Help?**

If you encounter issues not covered here:
1. Check logs: `tail -f logs/server.log`
2. Run diagnostics: `python3 scripts/health_check.py --verbose`
3. Report issues on GitHub with performance logs attached
