# Thesis Results - Quick Start Guide

## Quick Start

### Run All Tests with One Command

```bash
cd /home/user/HyFuzz/thesis_results

# Run all tests (approximately 15-20 minutes)
python3 run_all_tests.py

# Analyze results
python3 analysis_scripts/analyze_results.py

# Generate plots
python3 analysis_scripts/plot_results.py
```

### Step by Step Execution

#### 1. Modbus/TCP Tests

```bash
# Test validity and exception analysis
python3 modbus_tests/test_modbus_validity.py

# Test fuzzing performance
python3 modbus_tests/test_modbus_fuzzing.py
```

**Output Location:** `results_data/modbus_validity/` and `results_data/modbus_fuzzing/`

**Test Metrics:**
- PSR (Protocol Success Rate)
- EXR (Exception Rate)
- State Coverage (FC × address × unit-id)
- Crash Discovery
- Throughput (exec/s)

#### 2. CoAP Tests (with DTLS)

```bash
# Test coherence, ACK, response mix
python3 coap_tests/test_coap_validity.py

# Test fuzzing (DTLS comparison)
python3 coap_tests/test_coap_fuzzing.py
```

**Output Location:** `results_data/coap_validity/` and `results_data/coap_fuzzing/`

**Test Metrics:**
- MID/Token Coherence
- ACK Ratio
- Response Code Distribution (2xx/4xx/5xx)
- Observe Registration/Notification Cycles
- Blockwise Transfer Completions
- DTLS Overhead Analysis

#### 3. Baseline Comparisons

```bash
# Compare HyFuzz vs AFL/AFL++/AFLNet/libFuzzer/Grammar-based
python3 baseline_comparisons/compare_baselines.py
```

**Output Location:** `results_data/baseline_comparison/`

**Comparison Metrics:**
- Bug-Finding Effectiveness
- Code Coverage
- Execution Throughput
- Effect Sizes and Confidence Intervals

#### 4. Results Analysis and Visualization

```bash
# Step 1: Analyze all results
python3 analysis_scripts/analyze_results.py
# Output: results_data/analysis_summary.json
#         results_data/summary.txt

# Step 2: Generate plots (300 DPI publication quality)
python3 analysis_scripts/plot_results.py
# Output: plots/*.png
```

## Test Coverage Mapping to Thesis Chapters

### Corresponding to Results Chapter:

| Thesis Section | Test Script | Output File |
|---------------|-------------|-------------|
| §5.3.1 Modbus Validity | `test_modbus_validity.py` | `modbus_validity_results.json` |
| §5.3.2 Modbus State Progress | `test_modbus_validity.py` | `modbus_state_progress.json` |
| §5.3.3 Modbus Bug-Finding | `test_modbus_fuzzing.py` | `modbus_fuzzing_results.json` |
| §5.3.4 Modbus Efficiency | `test_modbus_fuzzing.py` | `modbus_fuzzing_results.json` |
| §5.4.1 CoAP Coherence/ACKs | `test_coap_validity.py` | `coap_validity_results.json` |
| §5.4.2 CoAP State Progress | `test_coap_validity.py` | `coap_validity_results.json` |
| §5.4.3 CoAP Bug-Finding | `test_coap_fuzzing.py` | `coap_fuzzing_results.json` |
| §5.4.4 CoAP Efficiency | `test_coap_fuzzing.py` | `coap_fuzzing_results.json` |
| §5.4.6 CoAP DTLS Impact | `test_coap_fuzzing.py` | `coap_fuzzing_results.json` |
| §5.3.5 & §5.4.5 Baselines | `compare_baselines.py` | `baseline_comparison_results.json` |

## Generated Plots

Running `plot_results.py` generates the following plots:

1. **modbus_psr_exr.png** - Modbus PSR vs EXR (by function code)
2. **modbus_state_coverage.png** - Modbus State Coverage Growth
3. **coap_coherence_dtls.png** - CoAP Coherence Metrics (DTLS Impact)
4. **baseline_comparison_modbus.png** - Modbus Baseline Comparison
5. **baseline_comparison_coap.png** - CoAP Baseline Comparison
6. **fuzzing_efficiency.png** - Fuzzing Efficiency Comparison

All plots are generated at 300 DPI for direct use in thesis.

## Expected Runtime

| Test | Estimated Time |
|------|----------------|
| Modbus Validity | 2-3 minutes |
| Modbus Fuzzing | 5 minutes |
| CoAP Validity | 3-4 minutes |
| CoAP Fuzzing | 6 minutes |
| Baseline Comparison | 10-12 minutes |
| **Total** | **~15-20 minutes** |

## Checking Results

```bash
# View results directory
ls -R results_data/

# View summary
cat results_data/summary.txt

# View generated plots
ls plots/
```

## Using Results in Your Thesis

### Table Data

The `results_data/summary.txt` file contains data that can be directly referenced:

```
PSR: 85.2%
EXR: 12.3%
Mean Latency: 3.45 ms
...
```

### Plot References

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\linewidth]{plots/modbus_psr_exr.png}
  \caption{Modbus Protocol Success vs Exception Rate by Function Code}
  \label{fig:modbus-psr-exr}
\end{figure}
```

## Customizing Parameters

To modify test parameters, edit the `main()` function in each script:

```python
# Example: Increase number of trials
await tester.run_all_tests(num_trials=2000)  # Default: 1000

# Example: Extend fuzzing duration
await tester.multi_trial_campaign(num_trials=10, duration_per_trial=120)  # Default: 5, 60
```

## Troubleshooting

### 1. Import Errors
```bash
# Ensure you're running from the correct directory
cd /home/user/HyFuzz/thesis_results
```

### 2. Missing Dependencies
```bash
# Install plotting libraries (only needed for plotting)
pip3 install matplotlib numpy seaborn
```

### 3. Permission Issues
```bash
# Ensure result directories are writable
chmod -R 755 results_data/ plots/
```

## Need Help?

For detailed documentation, see: `README.md`
