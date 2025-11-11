# Advanced Testing Suite Guide

**Comprehensive enhancement tests for thesis research**

---

## 📋 Table of Contents

1. [High-Priority Tests](#high-priority-tests)
2. [Medium-Priority Tests](#medium-priority-tests)
3. [Running the Tests](#running-the-tests)
4. [Results Interpretation](#results-interpretation)
5. [Thesis Integration](#thesis-integration)

---

## 🎯 High-Priority Tests

### 1. Long-term Stability Testing ⭐⭐⭐⭐⭐

**Purpose:** Detect memory leaks, performance degradation, and resource exhaustion

**Script:** `modbus_tests/test_long_term_stability.py`

**Duration:** 6-24 hours (configurable)

**Usage:**
```bash
# Full 6-hour test (default)
python3 modbus_tests/test_long_term_stability.py

# 24-hour test
python3 modbus_tests/test_long_term_stability.py --duration 24

# Quick test (10 minutes for validation)
python3 modbus_tests/test_long_term_stability.py --quick
```

**What It Tests:**
- Memory growth rate (MB per hour)
- Throughput degradation over time
- Crash discovery saturation
- CPU stability
- Resource leak detection

**Expected Results:**
- Stability Score: 90-100 (excellent), 70-90 (good), 50-70 (fair), <50 (poor)
- Memory growth rate: <5 MB/hour (acceptable)
- Throughput degradation: <5% per hour (acceptable)
- No memory leaks detected for production-ready systems

**Thesis Integration (§5.7):**
```latex
\subsection{Long-term Stability}
HyFuzz maintained stable performance over 24-hour continuous fuzzing,
with memory growth rate of X MB/hour and throughput degradation of Y\%.
Stability score of Z/100 indicates [excellent|good|fair|poor] long-term
robustness suitable for production deployment.
```

---

### 2. Coverage Analysis ⭐⭐⭐⭐

**Purpose:** Measure actual code coverage achieved by fuzzing strategies

**Script:** `modbus_tests/test_coverage_analysis.py`

**Duration:** ~7 minutes (5 configurations × 5 trials × 60s each)

**Usage:**
```bash
python3 modbus_tests/test_coverage_analysis.py
```

**What It Tests:**
- Line coverage percentage
- Branch coverage percentage
- Function coverage percentage
- Coverage growth curves
- Strategy comparison (random/guided/hybrid)
- Saturation point detection

**Expected Results:**
- Line coverage: 60-80% for guided fuzzing
- Branch coverage: 40-60% for guided fuzzing
- Hybrid strategy typically achieves best overall coverage
- Saturation at ~500-2000 executions

**Thesis Integration (§5.3.2, §5.4.2):**
```latex
\subsection{Coverage Analysis}
Hybrid fuzzing strategy achieved X\% line coverage and Y\% branch coverage,
outperforming random fuzzing by Z\% (Cohen's d = W, p < 0.001).
Coverage saturation occurred at approximately N executions.
```

---

### 3. Network Condition Testing ⭐⭐⭐⭐

**Purpose:** Test robustness under realistic network impairments

**Script:** `coap_tests/test_network_conditions.py`

**Duration:** ~12 minutes (12 conditions × 60s)

**Usage:**
```bash
python3 coap_tests/test_network_conditions.py
```

**What It Tests:**
- High latency scenarios (50ms, 100ms, 200ms RTT)
- Packet loss (1%, 5%, 10%)
- Bandwidth limitations (10 Mbps, 1 Mbps)
- Combined realistic scenarios (3G, 4G, poor WiFi)
- Throughput degradation
- Timeout behavior
- Retry mechanisms

**Expected Results:**
- Perfect network: ~180 req/s baseline
- High latency (200ms): 40-60% throughput reduction
- High packet loss (10%): 70-80% throughput reduction
- 3G mobile: 60-70% throughput reduction

**Thesis Integration (§5.9):**
```latex
\subsection{Network Robustness}
HyFuzz demonstrated resilience to network impairments. Under high latency
(200ms RTT), throughput decreased by X\% while maintaining Y\% success rate.
Under 10\% packet loss, the system maintained Z\% effectiveness through
automatic retry mechanisms.
```

---

### 4. Concurrent Client Testing ⭐⭐⭐

**Purpose:** Test scalability and race condition detection

**Script:** `modbus_tests/test_concurrent_clients.py`

**Duration:** ~10 minutes (8 configurations × 60s)

**Usage:**
```bash
python3 modbus_tests/test_concurrent_clients.py
```

**What It Tests:**
- Scalability with 1, 2, 4, 8, 16 concurrent clients
- Linear scaling efficiency
- Race condition detection
- Resource contention
- Same-target vs different-target modes

**Expected Results:**
- 1 client: ~5000 req/s baseline
- 4 clients: 95-100% scaling efficiency (same target)
- 8 clients: 85-95% scaling efficiency (same target)
- 16 clients: 70-85% scaling efficiency (contention visible)
- Different targets: >95% scaling efficiency

**Thesis Integration (§5.8):**
```latex
\subsection{Scalability Analysis}
HyFuzz achieved X\% scaling efficiency with 8 concurrent clients,
demonstrating near-linear scalability. At 16 clients, efficiency decreased
to Y\% due to resource contention. Z race conditions were detected and
handled gracefully.
```

---

### 5. Dictionary Effectiveness ⭐⭐⭐⭐

**Purpose:** Evaluate dictionary-based fuzzing impact

**Script:** `modbus_tests/test_dictionary_effectiveness.py`

**Duration:** ~5 minutes (5 dictionaries × 60s)

**Usage:**
```bash
python3 modbus_tests/test_dictionary_effectiveness.py
```

**What It Tests:**
- No dictionary (baseline)
- Protocol keywords only
- Protocol keywords + common values
- Learned dictionary
- Combined approach
- Crash discovery efficiency
- Coverage improvement
- Throughput impact

**Expected Results:**
- No dictionary: baseline crash discovery
- Protocol keywords: +10-20% crash improvement
- Protocol + values: +25-35% crash improvement
- Combined: +30-40% crash improvement
- Throughput cost: 10-15% slower with dictionary

**Thesis Integration (§5.3.6, §5.4.6):**
```latex
\subsection{Dictionary-based Fuzzing}
Dictionary-enhanced fuzzing increased crash discovery by X\% (p < 0.01)
at a Y\% throughput cost. The combined dictionary (protocol keywords +
common values) achieved optimal cost-benefit ratio of Z crashes per
1000 executions.
```

---

### 6. Resource Usage Profiling ⭐⭐⭐⭐

**Purpose:** Detailed resource consumption analysis

**Script:** `analysis_scripts/profile_resource_usage.py`

**Duration:** ~5 minutes (quick profile)

**Usage:**
```bash
# Quick 5-minute profile
python3 analysis_scripts/profile_resource_usage.py

# Custom duration (in seconds)
# Note: Edit script to change duration parameter
```

**What It Tests:**
- CPU utilization (mean, peak, stability)
- Memory usage (baseline, peak, growth)
- Disk I/O (read/write rates)
- Network I/O (send/receive rates)
- Thread count
- File descriptor usage
- Bottleneck identification

**Expected Results:**
- CPU usage: 20-40% mean (single-threaded fuzzing)
- Memory growth: <5% over test duration
- Disk I/O: Minimal (<1 MB/s)
- Network I/O: Depends on test rate
- No bottlenecks detected for well-configured systems

**Thesis Integration (§5.3.4, §5.4.4):**
```latex
\subsection{Resource Efficiency}
HyFuzz consumed an average of X\% CPU and Y MB memory during fuzzing
campaigns. Peak memory usage was Z MB with <W\% growth over 5-hour period.
No resource bottlenecks were identified, indicating efficient implementation.
```

---

### 7. Error Recovery Testing ⭐⭐

**Purpose:** Validate graceful degradation and recovery

**Script:** `modbus_tests/test_error_recovery.py`

**Duration:** ~10 minutes (5 scenarios × 120s)

**Usage:**
```bash
python3 modbus_tests/test_error_recovery.py
```

**What It Tests:**
- Target crash recovery
- Target restart handling
- Network disconnection recovery
- Resource exhaustion recovery
- Corrupted state recovery
- Recovery time
- Data loss quantification

**Expected Results:**
- Target crash: 95% recovery success, <5 test cases lost
- Target restart: 98% recovery success, 5-15 test cases lost
- Network disconnect: 90% recovery success
- Resource exhaustion: 85% recovery success
- Overall resilience score: 85-95%

**Thesis Integration (§5.10):**
```latex
\subsection{Fault Tolerance}
HyFuzz demonstrated robust error recovery with X\% overall success rate
across five failure scenarios. Target crash recovery succeeded in Y\%
of cases with mean recovery time of Z seconds and minimal data loss
(W test cases per failure).
```

---

## 🔬 Medium-Priority Tests

### 8. Protocol Version Testing

**Purpose:** Test effectiveness across protocol versions

**Script:** `analysis_scripts/test_protocol_versions.py`

**Duration:** ~12 minutes

**Usage:**
```bash
python3 analysis_scripts/test_protocol_versions.py
```

**What It Tests:**
- Modbus variants (TCP, RTU, ASCII)
- CoAP versions (RFC 7252, Draft-23, + extensions)
- DTLS versions (1.0, 1.2, 1.3)
- Version-specific bug discovery
- Maturity impact on bug density

**Expected Results:**
- Older versions typically have higher bug density
- Version-specific bugs: 20-30% of total
- DTLS 1.3 shows lowest bug density (modern, secure)

**Thesis Integration (§5.11):**
```latex
\subsection{Protocol Version Analysis}
Testing across protocol versions revealed X bugs in Modbus TCP vs Y in
Modbus ASCII. DTLS 1.3 demonstrated Z\% lower bug density compared to
DTLS 1.0, reflecting improved security and maturity.
```

---

### 9. Crash Triage Automation

**Purpose:** Automated crash classification and prioritization

**Script:** `analysis_scripts/automate_crash_triage.py`

**Duration:** <1 minute (analysis only)

**Usage:**
```bash
python3 analysis_scripts/automate_crash_triage.py
```

**What It Tests:**
- Automatic deduplication
- Severity classification (critical/high/medium/low)
- Exploitability assessment
- Root cause identification
- Priority scoring

**Expected Results:**
- Deduplication: 30-50% reduction in crash count
- Critical severity: 5-10% of unique crashes
- High severity: 20-30% of unique crashes
- Exploitable: 10-20% of unique crashes

**Thesis Integration (§5.12):**
```latex
\subsection{Automated Triage}
Automated crash triage reduced X crashes to Y unique bugs (Z\% deduplication).
Severity classification identified W critical vulnerabilities requiring
immediate attention. Exploitability assessment rated V\% as potentially
exploitable.
```

---

### 10. Real Implementation Comparison

**Purpose:** Compare against real-world implementations

**Script:** `baseline_comparisons/compare_real_implementations.py`

**Duration:** ~20 minutes (4 implementations × 5 min)

**Usage:**
```bash
python3 baseline_comparisons/compare_real_implementations.py
```

**What It Tests:**
- libmodbus vulnerability discovery
- libcoap vulnerability discovery
- pymodbus vulnerability discovery
- modbuspal vulnerability discovery
- Known CVE rediscovery rate
- False positive rate

**Expected Results:**
- Known CVE rediscovery: 60-80%
- False positive rate: <20%
- libmodbus typically shows more bugs (mature, complex)

**Thesis Integration (§5.13):**
```latex
\subsection{Real-world Validation}
Testing against real implementations (libmodbus, libcoap) rediscovered
X\% of known CVEs, validating fuzzer effectiveness. False positive rate
of Y\% demonstrates practical applicability. HyFuzz discovered Z previously
unknown bugs in modbuspal.
```

---

## 🚀 Running the Tests

### Quick Test Suite (30 minutes)

Run subset of tests with reduced durations:

```bash
# Long-term stability (quick mode - 10 min)
python3 modbus_tests/test_long_term_stability.py --quick

# Coverage analysis (7 min)
python3 modbus_tests/test_coverage_analysis.py

# Network conditions (12 min)
python3 coap_tests/test_network_conditions.py

# Total: ~30 minutes
```

### Comprehensive Test Suite (2-3 hours)

Run all enhancement tests:

```bash
cd /home/user/HyFuzz/thesis_results

# High-priority tests (~50 min)
python3 modbus_tests/test_long_term_stability.py  # 6+ hours optional
python3 modbus_tests/test_coverage_analysis.py
python3 coap_tests/test_network_conditions.py
python3 modbus_tests/test_concurrent_clients.py
python3 modbus_tests/test_dictionary_effectiveness.py
python3 analysis_scripts/profile_resource_usage.py
python3 modbus_tests/test_error_recovery.py

# Medium-priority tests (~35 min)
python3 analysis_scripts/test_protocol_versions.py
python3 analysis_scripts/automate_crash_triage.py
python3 baseline_comparisons/compare_real_implementations.py
```

### Parallel Execution

Some tests can run in parallel:

```bash
# Terminal 1: Long-term stability
python3 modbus_tests/test_long_term_stability.py &

# Terminal 2: Coverage + Network
python3 modbus_tests/test_coverage_analysis.py && \
python3 coap_tests/test_network_conditions.py &

# Terminal 3: Concurrent + Dictionary
python3 modbus_tests/test_concurrent_clients.py && \
python3 modbus_tests/test_dictionary_effectiveness.py &
```

---

## 📊 Results Interpretation

### Result Locations

All results are saved to `results_data/`:

```
results_data/
├── long_term_stability/
│   └── stability_6h_results.json
├── coverage_analysis/
│   └── coverage_analysis_results.json
├── network_conditions/
│   └── network_conditions_results.json
├── concurrent_clients/
│   └── concurrent_clients_results.json
├── dictionary_effectiveness/
│   └── dictionary_effectiveness_results.json
├── resource_profiling/
│   └── resource_profile_*.json
├── error_recovery/
│   └── error_recovery_results.json
├── protocol_versions/
│   └── protocol_versions_results.json
├── crash_triage/
│   └── crash_triage_results.json
└── real_implementations/
    └── real_implementation_results.json
```

### Key Metrics to Extract

For each test, extract these metrics for thesis:

1. **Mean ± Stdev** (with confidence intervals)
2. **Effect sizes** (Cohen's d for comparisons)
3. **Statistical significance** (p-values where applicable)
4. **Practical significance** (% improvements)

### Example Result Extraction

```python
import json

# Load results
with open('results_data/coverage_analysis/coverage_analysis_results.json') as f:
    data = json.load(f)

# Extract for thesis
for strategy in data['strategies']:
    name = strategy['strategy']
    line_cov = strategy['aggregate']['line_coverage_percent']['mean']
    stdev = strategy['aggregate']['line_coverage_percent']['stdev']

    print(f"{name}: {line_cov:.1f}% ± {stdev:.1f}%")
```

---

## 📝 Thesis Integration

### Chapter Structure

```
Chapter 5: Evaluation
  5.1 Experimental Setup (existing)
  5.2 Basic Protocol Testing (existing)
  5.3 Modbus/TCP Evaluation
      5.3.1 Validity Testing (existing)
      5.3.2 Coverage Analysis (NEW - from coverage test)
      5.3.3 Fuzzing Effectiveness (existing)
      5.3.4 Resource Efficiency (NEW - from profiling)
      5.3.5 Mutation Impact (existing extended)
      5.3.6 Dictionary Effectiveness (NEW)
      5.3.7 Seed Sensitivity (from QUICK_ENHANCEMENTS)
  5.4 CoAP/DTLS Evaluation
      5.4.1 Validity Testing (existing)
      5.4.2 Coverage Analysis (NEW)
      5.4.3 Fuzzing Effectiveness (existing)
      5.4.4 Resource Efficiency (NEW)
      5.4.5 DTLS Overhead (existing extended)
      5.4.6 Dictionary Effectiveness (NEW)
  5.5 Baseline Comparison (existing)
  5.6 Reproducibility (existing extended)
  5.7 Long-term Stability (NEW - from stability test)
  5.8 Scalability Analysis (NEW - from concurrent test)
  5.9 Network Robustness (NEW - from network test)
  5.10 Fault Tolerance (NEW - from error recovery)
  5.11 Protocol Version Analysis (NEW - optional)
  5.12 Automated Triage (NEW - optional)
  5.13 Real-world Validation (NEW - optional)
  5.14 Discussion
```

### LaTeX Template for New Sections

```latex
\subsection{Long-term Stability}

To evaluate long-term robustness, we executed continuous fuzzing campaigns
for 24 hours, monitoring memory usage, throughput, and crash discovery rates.

\textbf{Methodology:} The system was profiled every 5 minutes, measuring
RSS memory, CPU utilization, and execution throughput. Memory leak detection
employed linear regression on memory growth patterns.

\textbf{Results:} HyFuzz maintained stable performance throughout the
24-hour test period:

\begin{itemize}
    \item Memory growth: 2.3 MB/hour (0.5\% per hour)
    \item Throughput degradation: -1.2\% per hour
    \item Stability score: 94.7/100 (excellent)
    \item No memory leaks detected
\end{itemize}

\textbf{Analysis:} The minimal memory growth (0.5\%/hour) and negligible
throughput degradation (-1.2\%/hour) demonstrate production-ready stability.
The stability score of 94.7/100 indicates excellent long-term robustness
suitable for extended fuzzing campaigns.

\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\linewidth]{figures/stability_over_time.pdf}
  \caption{Memory and throughput stability over 24-hour fuzzing campaign}
  \label{fig:stability}
\end{figure}
```

### Statistical Reporting Template

Always include:
1. Mean ± standard deviation
2. 95% confidence intervals (if applicable)
3. Effect size (Cohen's d for comparisons)
4. Statistical significance (p-value)
5. Sample size (n = X trials)

Example:
> HyFuzz achieved 67.3% ± 3.2% line coverage (95% CI: [64.1%, 70.5%], n=5),
> significantly higher than AFL's 42.1% ± 2.8% (Cohen's d = 8.6, p < 0.001).

---

## ✅ Quality Checklist

Before finalizing thesis chapter:

### Data Quality
- [ ] All tests run successfully
- [ ] Sufficient sample sizes (n ≥ 3 for exploratory, n ≥ 5 for main results)
- [ ] Confidence intervals calculated
- [ ] Effect sizes computed for comparisons
- [ ] Statistical significance tested where appropriate
- [ ] Results reproducible (CV < 15%)

### Documentation
- [ ] All test parameters documented
- [ ] Result interpretation provided
- [ ] Limitations acknowledged
- [ ] Future work identified

### Thesis Integration
- [ ] Figures generated (if applicable)
- [ ] Tables formatted
- [ ] Statistical reporting complete
- [ ] Related work connected
- [ ] Contributions clearly stated

---

## 🎯 Expected Thesis Impact

**With Basic Tests Only:**
- Complete functional validation
- Baseline performance metrics
- Grade potential: B+/A-

**With Basic + Extended Tests:**
- Statistical rigor (CI, effect sizes)
- Multiple configurations tested
- Grade potential: A-/A

**With Basic + Extended + Enhancements:**
- Comprehensive evaluation
- Publication-quality analysis
- Long-term stability validation
- Scalability demonstration
- Robustness under impairments
- **Grade potential: A/A+**

---

## 📚 Additional Resources

### Result Analysis
- Use `analysis_scripts/statistical_analysis.py` for advanced statistics
- Use `analysis_scripts/create_visualizations.py` for plots

### Documentation
- See `EXTENDED_TESTS_GUIDE.md` for extended test details
- See `QUICK_ENHANCEMENTS.md` for quick-win improvements
- See `COMMANDS.md` for complete command reference

### Support
- All scripts include `--help` option
- Example output included in each script
- Validation modes available (e.g., `--quick`)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Status:** Complete and ready for use
