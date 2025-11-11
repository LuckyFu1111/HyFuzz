# Complete Command Reference

## All Commands Quick Reference

### One-Command Run

```bash
# Run all tests + analysis + plotting
cd /home/user/HyFuzz/thesis_results && \
python3 run_all_tests.py && \
python3 analysis_scripts/analyze_results.py && \
python3 analysis_scripts/plot_results.py
```

---

## Categorized Commands

### 1. Modbus/TCP Tests

#### 1.1 Validity Tests
```bash
# Basic run
python3 modbus_tests/test_modbus_validity.py

# Custom trial count
python3 -c "
import asyncio
from modbus_tests.test_modbus_validity import ModbusValidityTester
from pathlib import Path
async def run():
    tester = ModbusValidityTester(Path('results_data/modbus_validity'))
    await tester.run_all_tests(num_trials=2000)  # Customize to 2000
asyncio.run(run())
"
```

**Output Files:**
- `results_data/modbus_validity/modbus_validity_results.json`
- `results_data/modbus_validity/modbus_state_progress.json`

**Key Metrics:**
- `PSR` - Protocol Success Rate
- `EXR` - Exception Rate
- `per_function_code` - Per function code detailed data
- `unique_states` - Number of unique states discovered
- `fc_address_coverage` - FC×address coverage

#### 1.2 Fuzzing Tests
```bash
# Basic run
python3 modbus_tests/test_modbus_fuzzing.py

# Custom parameters
python3 -c "
import asyncio
from modbus_tests.test_modbus_fuzzing import ModbusFuzzingTester
from pathlib import Path
async def run():
    tester = ModbusFuzzingTester(Path('results_data/modbus_fuzzing'))
    await tester.multi_trial_campaign(
        num_trials=10,           # 10 trials
        duration_per_trial=120   # 120 seconds each
    )
asyncio.run(run())
"
```

**Output Files:**
- `results_data/modbus_fuzzing/modbus_fuzzing_results.json`

**Key Metrics:**
- `aggregate.execs.mean` - Mean execution count
- `aggregate.unique_crashes.mean` - Mean unique crashes
- `aggregate.throughput_exec_per_sec.mean` - Mean throughput

---

### 2. CoAP Tests

#### 2.1 Validity & Coherence Tests
```bash
# Basic run (tests both DTLS ON and OFF)
python3 coap_tests/test_coap_validity.py

# Test only without DTLS
python3 -c "
import asyncio
from coap_tests.test_coap_validity import CoAPValidityTester
from pathlib import Path
async def run():
    tester = CoAPValidityTester(Path('results_data/coap_validity'))
    result = await tester.test_coherence_and_acks(num_trials=1000, dtls_enabled=False)
    print(f'ACK Ratio: {result[\"ack_ratio\"]:.2%}')
asyncio.run(run())
"

# Test only Observe & Blockwise
python3 -c "
import asyncio
from coap_tests.test_coap_validity import CoAPValidityTester
from pathlib import Path
async def run():
    tester = CoAPValidityTester(Path('results_data/coap_validity'))
    result = await tester.test_observe_and_blockwise(num_trials=500, dtls_enabled=False)
    print(f'Observe Registrations: {result[\"observe\"][\"registration_success\"]}')
asyncio.run(run())
"
```

**Output Files:**
- `results_data/coap_validity/coap_validity_results.json`

**Key Metrics:**
- `ack_ratio` - ACK ratio
- `token_coherence_rate` - Token coherence
- `response_mix` - Response code distribution (2xx/4xx/5xx)
- `observe.registration_success` - Successful Observe registrations
- `blockwise.block1_completions` - Block1 completions

#### 2.2 Fuzzing Tests and DTLS Comparison
```bash
# Basic run
python3 coap_tests/test_coap_fuzzing.py

# Run DTLS impact comparison separately
python3 -c "
import asyncio
from coap_tests.test_coap_fuzzing import CoAPFuzzingTester
from pathlib import Path
async def run():
    tester = CoAPFuzzingTester(Path('results_data/coap_fuzzing'))
    result = await tester.compare_dtls_impact(num_trials=5, duration_per_trial=90)
    print(f'DTLS Overhead: {result[\"comparison\"][\"dtls_overhead_percent\"]:.1f}%')
asyncio.run(run())
"
```

**Output Files:**
- `results_data/coap_fuzzing/coap_fuzzing_results.json`

**Key Metrics:**
- `comparison.dtls_overhead_percent` - DTLS overhead percentage
- `no_dtls_trials` - No DTLS trial results
- `with_dtls_trials` - With DTLS trial results

---

### 3. Baseline Comparison

```bash
# Basic run (compare all fuzzers)
python3 baseline_comparisons/compare_baselines.py

# Compare Modbus only
python3 -c "
import asyncio
from baseline_comparisons.compare_baselines import BaselineComparer
from pathlib import Path
async def run():
    comparer = BaselineComparer(Path('results_data/baseline_comparison'))
    result = await comparer.compare_on_target('modbus', duration_per_trial=60, num_trials=3)
    effects = comparer.calculate_effect_sizes(result)
    for metric, data in effects.items():
        print(f'{metric}: {data[\"improvement_percent\"]:+.1f}%')
asyncio.run(run())
"

# Compare CoAP only
python3 -c "
import asyncio
from baseline_comparisons.compare_baselines import BaselineComparer
from pathlib import Path
async def run():
    comparer = BaselineComparer(Path('results_data/baseline_comparison'))
    result = await comparer.compare_on_target('coap', duration_per_trial=60, num_trials=3)
asyncio.run(run())
"
```

**Output Files:**
- `results_data/baseline_comparison/baseline_comparison_results.json`

**Compared Fuzzers:**
- AFL (baseline)
- AFL++
- AFLNet (protocol-aware)
- libFuzzer
- Grammar-based
- HyFuzz

**Key Metrics:**
- `effect_sizes.unique_crashes.improvement_percent` - Crash finding improvement
- `effect_sizes.coverage.improvement_percent` - Coverage improvement
- `fuzzer_rankings` - Fuzzer rankings

---

### 4. Results Analysis

#### 4.1 Data Analysis
```bash
# Full analysis
python3 analysis_scripts/analyze_results.py

# View summary
cat results_data/summary.txt

# View JSON data
cat results_data/analysis_summary.json | python3 -m json.tool

# Extract specific metrics
python3 -c "
import json
with open('results_data/analysis_summary.json') as f:
    data = json.load(f)
    print('Modbus PSR:', data['modbus']['validity']['PSR'])
    print('CoAP ACK Ratio (no DTLS):', data['coap']['coherence_no_dtls']['ack_ratio'])
"
```

**Output Files:**
- `results_data/analysis_summary.json` - Structured analysis
- `results_data/summary.txt` - Text summary

#### 4.2 Generate Plots
```bash
# Generate all plots
python3 analysis_scripts/plot_results.py

# View generated plots
ls -lh plots/

# Use in LaTeX
echo "\\includegraphics[width=0.9\\linewidth]{plots/modbus_psr_exr.png}"
```

**Generated Plots (300 DPI):**
1. `modbus_psr_exr.png` - Modbus PSR vs EXR
2. `modbus_state_coverage.png` - State coverage growth
3. `coap_coherence_dtls.png` - CoAP coherence (DTLS impact)
4. `baseline_comparison_modbus.png` - Modbus baseline comparison
5. `baseline_comparison_coap.png` - CoAP baseline comparison
6. `fuzzing_efficiency.png` - Fuzzing efficiency

---

### 5. Batch Commands

#### 5.1 Run All Modbus Tests
```bash
python3 modbus_tests/test_modbus_validity.py && \
python3 modbus_tests/test_modbus_fuzzing.py
```

#### 5.2 Run All CoAP Tests
```bash
python3 coap_tests/test_coap_validity.py && \
python3 coap_tests/test_coap_fuzzing.py
```

#### 5.3 Complete Workflow (Test + Analysis + Plotting)
```bash
# Full run
cd /home/user/HyFuzz/thesis_results

# Step 1: All tests
python3 run_all_tests.py

# Step 2: Analysis
python3 analysis_scripts/analyze_results.py

# Step 3: Plotting
python3 analysis_scripts/plot_results.py

# Step 4: View results
cat results_data/summary.txt
ls plots/
```

---

### 6. Data Query Commands

#### 6.1 Modbus Data Queries
```bash
# Query PSR
python3 -c "
import json
with open('results_data/modbus_validity/modbus_validity_results.json') as f:
    data = json.load(f)
    print(f'PSR: {data[\"PSR\"]:.2%}')
    print(f'EXR: {data[\"EXR\"]:.2%}')
"

# Query unique states
python3 -c "
import json
with open('results_data/modbus_validity/modbus_state_progress.json') as f:
    data = json.load(f)
    print(f'Unique States: {data[\"unique_states\"]}')
"

# Query average crashes
python3 -c "
import json
with open('results_data/modbus_fuzzing/modbus_fuzzing_results.json') as f:
    data = json.load(f)
    print(f'Mean Crashes: {data[\"aggregate\"][\"unique_crashes\"][\"mean\"]:.1f}')
"
```

#### 6.2 CoAP Data Queries
```bash
# Query ACK ratio
python3 -c "
import json
with open('results_data/coap_validity/coap_validity_results.json') as f:
    data = json.load(f)
    print(f'ACK Ratio (no DTLS): {data[\"coherence_no_dtls\"][\"ack_ratio\"]:.2%}')
    print(f'ACK Ratio (with DTLS): {data[\"coherence_with_dtls\"][\"ack_ratio\"]:.2%}')
"

# Query DTLS overhead
python3 -c "
import json
with open('results_data/coap_fuzzing/coap_fuzzing_results.json') as f:
    data = json.load(f)
    print(f'DTLS Overhead: {data[\"comparison\"][\"dtls_overhead_percent\"]:.1f}%')
"
```

#### 6.3 Baseline Comparison Queries
```bash
# Query improvement percentages
python3 -c "
import json
with open('results_data/baseline_comparison/baseline_comparison_results.json') as f:
    data = json.load(f)
    effects = data['modbus']['effect_sizes']
    for metric, values in effects.items():
        print(f'{metric}: {values[\"improvement_percent\"]:+.1f}%')
"
```

---

### 7. Cleanup Commands

```bash
# Clean all results
rm -rf results_data/* plots/*

# Clean plots only
rm -rf plots/*

# Clean specific test results
rm -rf results_data/modbus_validity/*
rm -rf results_data/coap_fuzzing/*
```

---

### 8. Debugging Commands

```bash
# Check directory structure
tree thesis_results/ -L 2

# Check script syntax
python3 -m py_compile modbus_tests/test_modbus_validity.py
python3 -m py_compile coap_tests/test_coap_validity.py

# Test individual function
python3 -c "
import asyncio
from modbus_tests.test_modbus_validity import ModbusValidityTester
from pathlib import Path
async def test():
    tester = ModbusValidityTester(Path('results_data/test'))
    result = await tester.test_validity_profiles(num_trials=10)
    print(result)
asyncio.run(test())
"
```

---

### 9. Performance Monitoring

```bash
# Monitor execution time
time python3 run_all_tests.py

# Monitor individual test
time python3 modbus_tests/test_modbus_validity.py

# Monitor memory usage
/usr/bin/time -v python3 run_all_tests.py
```

---

### 10. Generate Thesis Tables

```bash
# Generate LaTeX table data
python3 -c "
import json

# Load analysis data
with open('results_data/analysis_summary.json') as f:
    data = json.load(f)

# Modbus table
print('\\begin{table}[t]')
print('\\centering')
print('\\caption{Modbus/TCP Results Summary}')
print('\\begin{tabular}{lc}')
print('\\toprule')
print('Metric & Value \\\\')
print('\\midrule')
print(f'PSR & {data[\"modbus\"][\"validity\"][\"PSR\"]:.2%} \\\\\\\\')
print(f'EXR & {data[\"modbus\"][\"validity\"][\"EXR\"]:.2%} \\\\\\\\')
print(f'Unique States & {data[\"modbus\"][\"state_coverage\"][\"unique_states\"]} \\\\\\\\')
print('\\bottomrule')
print('\\end{tabular}')
print('\\end{table}')
"
```

---

## Common Workflows

### Workflow 1: Quick Test
```bash
# Quick validation (reduced trial count)
cd /home/user/HyFuzz/thesis_results
python3 -c "
import asyncio
from modbus_tests.test_modbus_validity import ModbusValidityTester
from pathlib import Path
async def quick_test():
    tester = ModbusValidityTester(Path('results_data/quick_test'))
    await tester.run_all_tests(num_trials=100)  # Only 100 trials
asyncio.run(quick_test())
"
```

### Workflow 2: Complete Thesis Data Collection
```bash
# Run all tests in sequence
cd /home/user/HyFuzz/thesis_results
python3 run_all_tests.py
python3 analysis_scripts/analyze_results.py
python3 analysis_scripts/plot_results.py

# Check results
cat results_data/summary.txt
ls -lh plots/
```

### Workflow 3: Update Plots Only
```bash
# If data already exists, regenerate plots only
cd /home/user/HyFuzz/thesis_results
python3 analysis_scripts/plot_results.py
```

---

## Environment Setup

```bash
# Install dependencies (if plotting is needed)
pip3 install matplotlib numpy seaborn

# Check Python version
python3 --version  # Requires 3.9+

# Check disk space
df -h /home/user/HyFuzz/thesis_results/
```

---

## Troubleshooting Commands

```bash
# Issue 1: Import errors
cd /home/user/HyFuzz/thesis_results
export PYTHONPATH="/home/user/HyFuzz/HyFuzz-Ubuntu-Client/src:$PYTHONPATH"

# Issue 2: Permission errors
chmod -R 755 /home/user/HyFuzz/thesis_results/
chmod +x *.py */*.py

# Issue 3: Results directories don't exist
mkdir -p results_data/{modbus_validity,modbus_fuzzing,coap_validity,coap_fuzzing,baseline_comparison}
mkdir -p plots/
```

---

**Tip:** Add commonly used commands to shell aliases:

```bash
# Add to ~/.bashrc
alias thesis-test='cd /home/user/HyFuzz/thesis_results && python3 run_all_tests.py'
alias thesis-analyze='cd /home/user/HyFuzz/thesis_results && python3 analysis_scripts/analyze_results.py'
alias thesis-plot='cd /home/user/HyFuzz/thesis_results && python3 analysis_scripts/plot_results.py'
alias thesis-summary='cat /home/user/HyFuzz/thesis_results/results_data/summary.txt'
```
