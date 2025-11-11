# Thesis Results Testing Suite

This directory contains all test scripts and analysis tools for the thesis results chapter.

## Directory Structure

```
thesis_results/
├── modbus_tests/              # Modbus/TCP protocol tests
│   ├── test_modbus_validity.py    # Validity and exception profiles
│   └── test_modbus_fuzzing.py     # Fuzzing campaigns
├── coap_tests/                # CoAP protocol tests (with DTLS)
│   ├── test_coap_validity.py      # Coherence, ACKs, response mix
│   └── test_coap_fuzzing.py       # Fuzzing with DTLS comparison
├── baseline_comparisons/      # Baseline fuzzer comparisons
│   └── compare_baselines.py       # AFL, AFL++, AFLNet, etc.
├── analysis_scripts/          # Data analysis and plotting
│   ├── analyze_results.py         # Aggregate analysis
│   └── plot_results.py            # Generate thesis plots
├── results_data/              # Output directory for test results
└── plots/                     # Output directory for plots
```

## Quick Start

### Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for basic tests
- **[EXTENDED_TESTS_GUIDE.md](EXTENDED_TESTS_GUIDE.md)** - Extended testing with statistical analysis
- **[ADVANCED_TESTS_GUIDE.md](ADVANCED_TESTS_GUIDE.md)** - ⭐ Advanced enhancements (NEW!)
- **[COMMANDS.md](COMMANDS.md)** - Complete command reference
- **[QUICK_ENHANCEMENTS.md](QUICK_ENHANCEMENTS.md)** - High-value quick wins

### Run All Basic Tests

```bash
# From the thesis_results directory
python3 run_all_tests_standalone.py
```

This will:
1. Run all Modbus tests
2. Run all CoAP tests
3. Run baseline comparisons
4. Analyze results
5. Generate plots

### Run Advanced Enhancement Tests (NEW!)

```bash
# See ADVANCED_TESTS_GUIDE.md for complete documentation

# High-priority enhancements
python3 modbus_tests/test_long_term_stability.py --quick  # 10 min quick test
python3 modbus_tests/test_coverage_analysis.py            # 7 min
python3 coap_tests/test_network_conditions.py             # 12 min
python3 modbus_tests/test_concurrent_clients.py           # 10 min
python3 modbus_tests/test_dictionary_effectiveness.py     # 5 min
python3 analysis_scripts/profile_resource_usage.py        # 5 min
python3 modbus_tests/test_error_recovery.py               # 10 min

# Medium-priority enhancements
python3 analysis_scripts/test_protocol_versions.py        # 12 min
python3 analysis_scripts/automate_crash_triage.py         # <1 min
python3 baseline_comparisons/compare_real_implementations.py  # 20 min
```

### Run Individual Test Suites

#### Modbus/TCP Tests

```bash
# Test 1: Validity and exception profiles (PSR vs EXR)
python3 modbus_tests/test_modbus_validity.py

# Test 2: Fuzzing campaign (bug-finding, efficiency)
python3 modbus_tests/test_modbus_fuzzing.py
```

**Output:**
- `results_data/modbus_validity/modbus_validity_results.json`
- `results_data/modbus_validity/modbus_state_progress.json`
- `results_data/modbus_fuzzing/modbus_fuzzing_results.json`

**Metrics collected:**
- Protocol Success Rate (PSR)
- Exception Rate (EXR)
- Per-function-code breakdown
- State coverage (FC × address × unit-id)
- Unique crashes
- Time to first crash (TTFC)
- Throughput (exec/s)

#### CoAP Tests (with DTLS)

```bash
# Test 1: Coherence, ACKs, and response mix
python3 coap_tests/test_coap_validity.py

# Test 2: Fuzzing with DTLS comparison
python3 coap_tests/test_coap_fuzzing.py
```

**Output:**
- `results_data/coap_validity/coap_validity_results.json`
- `results_data/coap_fuzzing/coap_fuzzing_results.json`

**Metrics collected:**
- MID/Token coherence rates
- ACK ratios
- Response code distribution (2xx/4xx/5xx)
- Observe registration/notification cycles
- Blockwise transfer completions (Block1/Block2)
- SZX diversity
- DTLS overhead analysis

#### Baseline Comparisons

```bash
# Compare HyFuzz vs AFL, AFL++, AFLNet, libFuzzer, Grammar-based
python3 baseline_comparisons/compare_baselines.py
```

**Output:**
- `results_data/baseline_comparison/baseline_comparison_results.json`

**Comparisons:**
- Bug-finding effectiveness (unique crashes)
- Code coverage
- Throughput (exec/s)
- Effect sizes with confidence intervals

### Analysis and Visualization

```bash
# Step 1: Analyze all results
python3 analysis_scripts/analyze_results.py

# Step 2: Generate plots
python3 analysis_scripts/plot_results.py
```

**Outputs:**

*Analysis:*
- `results_data/analysis_summary.json` - Structured analysis
- `results_data/summary.txt` - Text summary for thesis

*Plots (300 DPI, publication quality):*
- `plots/modbus_psr_exr.png` - PSR vs EXR by function code
- `plots/modbus_state_coverage.png` - State coverage growth
- `plots/coap_coherence_dtls.png` - DTLS impact on coherence
- `plots/baseline_comparison_modbus.png` - Modbus baseline comparison
- `plots/baseline_comparison_coap.png` - CoAP baseline comparison
- `plots/fuzzing_efficiency.png` - Throughput and efficiency

## Detailed Command Reference

### Modbus Validity Tests

```bash
# Run with custom parameters
python3 modbus_tests/test_modbus_validity.py

# The script tests:
# - 1000 validity trials (PSR/EXR measurement)
# - 500 stateful trials (state coverage)
# - All Modbus function codes (1-16, 23)
# - Address range: 0-65535
# - Count range: 1-125
```

**Expected runtime:** ~2-3 minutes

### Modbus Fuzzing Tests

```bash
# Run with default settings
python3 modbus_tests/test_modbus_fuzzing.py

# Configuration:
# - 5 trials
# - 60 seconds per trial
# - Medium mutation level
# - Tracks: crashes, exceptions, coverage, throughput
```

**Expected runtime:** ~5 minutes

### CoAP Validity Tests

```bash
# Run with default settings
python3 coap_tests/test_coap_validity.py

# Tests both DTLS modes:
# - WITHOUT DTLS: 1000 coherence trials + 500 milestone trials
# - WITH DTLS: 1000 coherence trials + 500 milestone trials
```

**Expected runtime:** ~3-4 minutes

### CoAP Fuzzing Tests

```bash
# Run with default settings
python3 coap_tests/test_coap_fuzzing.py

# Configuration:
# - 3 trials without DTLS
# - 3 trials with DTLS
# - 60 seconds per trial
# - Calculates DTLS overhead
```

**Expected runtime:** ~6 minutes

### Baseline Comparison

```bash
# Run with default settings
python3 baseline_comparisons/compare_baselines.py

# Compares 6 fuzzers:
# - AFL (baseline)
# - AFL++
# - AFLNet (protocol-aware)
# - libFuzzer
# - Grammar-based
# - HyFuzz

# On 2 targets:
# - Modbus/TCP
# - CoAP

# 3 trials × 60s per fuzzer per target
```

**Expected runtime:** ~10-12 minutes (simulated)

## Customization

### Adjust Test Parameters

Edit the `main()` function in each script:

```python
# In test_modbus_validity.py
await tester.run_all_tests(num_trials=2000)  # Increase trials

# In test_modbus_fuzzing.py
await tester.multi_trial_campaign(num_trials=10, duration_per_trial=120)  # More trials, longer duration

# In test_coap_validity.py
await tester.run_all_tests(num_trials=500)  # Reduce trials

# In compare_baselines.py
await comparer.run_all_comparisons()  # Uses defaults
```

### Mutation Levels

In fuzzing scripts, adjust mutation aggressiveness:

```python
# In generate_fuzz_params()
params = self.generate_fuzz_params(mutation_level="aggressive")
# Options: "low", "medium", "aggressive"
```

## Understanding Results

### Modbus Results

**Validity Results (`modbus_validity_results.json`):**
```json
{
  "PSR": 0.85,                    // Protocol Success Rate
  "EXR": 0.12,                    // Exception Rate
  "timeout_rate": 0.03,
  "per_function_code": {
    "1": {"PSR": 0.90, "EXR": 0.08},  // Per-FC breakdown
    ...
  }
}
```

**State Progress (`modbus_state_progress.json`):**
```json
{
  "unique_states": 245,           // Total unique states
  "fc_address_coverage": [...],   // (FC, address_bin) pairs
  "state_transitions": [          // Coverage growth timeline
    {"trial": 0, "coverage_size": 1},
    {"trial": 1, "coverage_size": 3},
    ...
  ]
}
```

**Fuzzing Results (`modbus_fuzzing_results.json`):**
```json
{
  "aggregate": {
    "execs": {"mean": 5234, "stdev": 123},
    "unique_crashes": {"mean": 3.2, "stdev": 0.8},
    "throughput_exec_per_sec": {"mean": 87.2}
  }
}
```

### CoAP Results

**Validity Results (`coap_validity_results.json`):**
```json
{
  "coherence_no_dtls": {
    "ack_ratio": 0.95,
    "token_coherence_rate": 0.99,
    "response_mix": {
      "2xx_percent": 0.75,
      "4xx_percent": 0.20,
      "5xx_percent": 0.05
    }
  },
  "milestones_no_dtls": {
    "observe": {
      "registration_success": 48,
      "notification_cycles": 42
    },
    "blockwise": {
      "block1_completions": 12,
      "block2_completions": 15,
      "szx_diversity": [16, 32, 64, 128, 256, 512, 1024]
    }
  }
}
```

### Baseline Comparison Results

**Comparison Results (`baseline_comparison_results.json`):**
```json
{
  "modbus": {
    "effect_sizes": {
      "unique_crashes": {
        "baseline_mean": 2.1,       // AFL
        "hyfuzz_mean": 3.2,         // HyFuzz
        "improvement_percent": 52.4  // +52.4%
      }
    }
  }
}
```

## Requirements

### Python Dependencies

```bash
# Core dependencies
pip3 install asyncio json statistics pathlib

# For plotting (optional, only if running plot_results.py)
pip3 install matplotlib numpy seaborn
```

### System Requirements

- Python 3.9+
- 2GB RAM minimum
- 500MB disk space for results

## Troubleshooting

### Common Issues

**1. Module import errors:**
```bash
# Solution: Ensure you're running from the thesis_results directory
cd /home/user/HyFuzz/thesis_results
python3 modbus_tests/test_modbus_validity.py
```

**2. No results generated:**
```bash
# Check that results_data directory exists and is writable
ls -la results_data/
```

**3. Plotting fails:**
```bash
# Install matplotlib dependencies
pip3 install matplotlib numpy
```

**4. Slow execution:**
```bash
# Reduce trial counts in scripts or run specific tests only
```

## Integration with Thesis

### Generating Tables

The `analyze_results.py` script generates summary tables suitable for LaTeX:

```bash
python3 analysis_scripts/analyze_results.py

# Output in results_data/summary.txt can be used directly
# or converted to LaTeX table format
```

### Using Plots in LaTeX

All plots are generated at 300 DPI (publication quality):

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\linewidth]{plots/modbus_psr_exr.png}
  \caption{Modbus Protocol Success vs Exception Rate by Function Code}
  \label{fig:modbus-psr-exr}
\end{figure}
```

## Citation

When referencing these results in your thesis:

```latex
Results were obtained using the HyFuzz thesis testing framework
with the following configuration: [describe parameters].
All experiments were conducted with k=\{3,5\} independent trials
to ensure statistical validity. Median values with interquartile
ranges (IQR) are reported throughout.
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the individual script docstrings
3. Examine the results JSON files for detailed data

## License

Part of the HyFuzz project. See main project LICENSE.
