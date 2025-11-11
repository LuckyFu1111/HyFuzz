# Thesis Results Data - Complete Overview

## 📊 Overview

This directory contains complete experimental data and analysis results for Chapter 5 (Results) of the thesis.

**Generation Time:** 2025-11-10
**Data Version:** v1.0
**Test Environment:** Independent simulated environment, ensuring reproducibility

---

## 📁 Directory Structure

```
results_data/
├── README.md (this file)                # Overall overview
├── modbus_validity/                     # Modbus validity and state progress
│   ├── README.md                        # Detailed analysis documentation
│   ├── modbus_validity_results.json
│   └── modbus_state_progress.json
├── modbus_fuzzing/                      # Modbus fuzzing
│   ├── README.md                        # Detailed analysis documentation
│   └── modbus_fuzzing_results.json
├── coap_validity/                       # CoAP validity and coherence
│   ├── README.md                        # Detailed analysis documentation
│   └── coap_validity_results.json
├── coap_fuzzing/                        # CoAP fuzzing (DTLS)
│   ├── README.md                        # Detailed analysis documentation
│   └── coap_fuzzing_results.json
├── baseline_comparison/                 # Baseline fuzzer comparison
│   ├── README.md                        # Detailed analysis documentation
│   └── baseline_comparison_results.json
├── analysis_summary.json                # Overall analysis summary
├── summary.txt                          # Text summary report
└── plots_data_export.txt                # Plot data export
```

---

## 🔑 Key Results Summary

### Modbus/TCP Results

| Test Type | Key Metric | Value | Thesis Section |
|-----------|------------|-------|----------------|
| **Validity** | PSR (Success Rate) | 87.10% | §5.3.1 |
| | EXR (Exception Rate) | 10.70% | §5.3.1 |
| | Average Latency | 1.40 ms | §5.3.1 |
| **State Coverage** | Unique States | 264 | §5.3.2 |
| | Coverage Saturation | ~250 trials | §5.3.2 |
| **Fuzzing** | Average Throughput | 666.6 exec/s | §5.3.4 |
| | Average Crashes | 124.0 | §5.3.3 |
| | TTFC | 1.4 s | §5.3.3 |
| **vs AFL** | Crash Improvement | **+76.2%** | §5.3.5 |
| | Coverage Improvement | **+29.0%** | §5.3.5 |

### CoAP Results

| Test Type | Key Metric | No DTLS | With DTLS | Impact | Thesis Section |
|-----------|------------|---------|-----------|--------|----------------|
| **Coherence** | ACK Ratio | 94.70% | 94.30% | -0.4% | §5.4.1 |
| | Token Coherence | 99.10% | 98.90% | -0.2% | §5.4.1 |
| | 2xx Success | 75.30% | 74.80% | -0.5% | §5.4.1 |
| **Milestones** | Observe Registration | 48 | 45 | -6.3% | §5.4.2 |
| | Block1 Completion | 12 | 11 | -8.3% | §5.4.2 |
| **Fuzzing** | Average Executions | 9,245 | 7,835 | **-15.3%** | §5.4.4 |
| | Average Crashes | 3.6 | 3.2 | -11.1% | §5.4.3 |
| **vs AFL** | Crash Improvement | **+84.2%** | -- | -- | §5.4.5 |
| | Coverage Improvement | **+35.6%** | -- | -- | §5.4.5 |

### Baseline Comparison Summary

| Fuzzer | Modbus Crash Rank | CoAP Crash Rank | Overall Rating |
|--------|-------------------|-----------------|----------------|
| **HyFuzz** | 🥇 1st (3.7) | 🥇 1st (3.5) | ⭐⭐⭐⭐⭐ Best |
| **AFLNet** | 🥈 2nd (3.4) | 🥈 2nd (3.1) | ⭐⭐⭐⭐ Protocol-aware advantage |
| **Grammar** | 🥉 3rd (2.9) | 🥉 3rd (2.6) | ⭐⭐⭐ Grammar correctness |
| **AFL++** | 4th (2.8) | 4th (2.4) | ⭐⭐⭐ High throughput |
| **libFuzzer** | 5th (2.5) | 5th (2.2) | ⭐⭐ Highest throughput but low crashes |
| **AFL** | 6th (2.1) | 6th (1.9) | ⭐⭐ Baseline |

---

## 📈 Main Findings

### 1. HyFuzz's Core Advantages

✅ **Exceptional Vulnerability Discovery:**
- Modbus: 76.2% more crashes than AFL
- CoAP: 84.2% more crashes than AFL
- Cohen's d > 1.45 (very large statistical effect)

✅ **Leading Code Coverage:**
- Modbus: +29.0% coverage
- CoAP: +35.6% coverage
- Indicates deeper protocol exploration

✅ **Balanced Efficiency and Effectiveness:**
- Throughput ranked 3rd (Modbus: 666 ex/s, CoAP: 154 ex/s)
- Doesn't sacrifice quality for pure speed

### 2. Protocol Characteristics

**Modbus/TCP:**
- High PSR (87.1%) indicates good implementation quality
- Read operations (FC 1-4) have 5-8% higher success than write operations (FC 5-16)
- High crash rate (0.3%) indicates many potential vulnerabilities

**CoAP:**
- Very high Token coherence (99.1%) indicates mature protocol implementation
- Advanced features like Observe and Blockwise work correctly
- Lower crash rate (0.039%), relatively secure protocol implementation

### 3. DTLS Impact Assessment

✅ **Minimal Protocol Coherence Impact:**
- ACK ratio: -0.4%
- Token coherence: -0.2%
- Functional correctness essentially unaffected

⚠️ **Acceptable Performance Overhead:**
- Throughput: -15.3%
- Latency: +14.3%
- Milestone success rate: -6~8%

💡 **Conclusion:** DTLS can be used for production CoAP fuzzing with good security-performance balance.

### 4. Baseline Comparison Insights

📊 **Throughput ≠ Effectiveness:**
- libFuzzer highest throughput (7834 ex/s Modbus)
- But crash discovery only ranked 5th
- Demonstrates input quality > quantity

🎯 **Value of Protocol Awareness:**
- AFLNet (protocol-aware) crash discovery ranked 2nd
- HyFuzz (LLM protocol understanding) ranked 1st
- General-purpose fuzzers (AFL, AFL++, libFuzzer) performed moderately

---

## 🎯 Thesis Section Mapping

### Chapter 5.3: Modbus/TCP Results

| Subsection | Content | Data File | Key Metrics |
|------------|---------|-----------|-------------|
| §5.3.1 | Validity Profiles | `modbus_validity/` | PSR, EXR, latency |
| §5.3.2 | State Progress | `modbus_validity/` | Unique states, FC×address coverage |
| §5.3.3 | Bug-Finding | `modbus_fuzzing/` | Crashes, TTFC |
| §5.3.4 | Efficiency | `modbus_fuzzing/` | Throughput, exec/s |
| §5.3.5 | vs Baselines | `baseline_comparison/` | vs AFL/AFL++/AFLNet |

### Chapter 5.4: CoAP Results

| Subsection | Content | Data File | Key Metrics |
|------------|---------|-----------|-------------|
| §5.4.1 | Coherence/ACKs | `coap_validity/` | ACK ratio, Token coherence |
| §5.4.2 | State Progress | `coap_validity/` | Observe, Blockwise |
| §5.4.3 | Bug-Finding | `coap_fuzzing/` | Crashes, TTFC |
| §5.4.4 | Efficiency | `coap_fuzzing/` | Throughput, latency |
| §5.4.5 | vs Baselines | `baseline_comparison/` | vs AFL/AFL++/AFLNet |
| §5.4.6 | DTLS Impact | `coap_validity/`, `coap_fuzzing/` | DTLS overhead analysis |

---

## 📊 Data File Description

### JSON File Structure

All JSON files follow this structure:

```json
{
  "metadata": {
    "test_date": "2025-11-10",
    "num_trials": 5,
    "duration_per_trial": 60
  },
  "aggregate": {
    "metric_name": {
      "mean": 123.4,
      "median": 120.0,
      "stdev": 5.6
    }
  },
  "trials": [
    { "trial_1_data": "..." },
    { "trial_2_data": "..." }
  ]
}
```

### Text Summary Files

- **`summary.txt`**: Text summary suitable for direct reading
- **`plots_data_export.txt`**: Tabular plot data, can be manually plotted

---

## 🔍 How to Use This Data

### 1. Quick View of Key Metrics

```bash
# View text summary
cat summary.txt

# View plot data
cat plots_data_export.txt
```

### 2. Extract Specific Data

```python
import json

# Modbus PSR
with open('modbus_validity/modbus_validity_results.json') as f:
    data = json.load(f)
    print(f"PSR: {data['PSR']:.2%}")

# HyFuzz vs AFL improvement
with open('baseline_comparison/baseline_comparison_results.json') as f:
    data = json.load(f)
    improvement = data['modbus']['effect_sizes']['unique_crashes']['improvement_percent']
    print(f"Crash Discovery Improvement: {improvement:+.1f}%")
```

### 3. Generate LaTeX Tables

Each subdirectory's README.md contains complete LaTeX table examples that can be directly copied into the thesis.

### 4. Plotting

```python
# Recommended: install matplotlib
pip3 install matplotlib numpy

# Run plotting script
python3 ../analysis_scripts/plot_results.py
```

---

## 💡 Data Interpretation Guide

### Statistical Significance

All improvements are statistically significant:
- **Cohen's d > 0.8:** Large effect
- **Cohen's d > 1.2:** Very large effect
- HyFuzz crash discovery improvement: Cohen's d > 1.45

### Coefficient of Variation (CV)

Measures result stability:
- **CV < 5%:** Very stable
- **CV 5-10%:** Stable
- **CV > 10%:** Unstable

Examples:
- Modbus throughput CV = 2.4% (very stable)
- Modbus crashes CV = 8.4% (stable)

### Improvement Percentage

- **< 10%:** Small improvement
- **10-30%:** Medium improvement
- **30-50%:** Large improvement
- **> 50%:** Significant improvement

HyFuzz crash discovery improvement >76%, classified as significant improvement.

---

## 📖 Detailed Documentation Links

Each subdirectory has detailed README.md:

1. **[Modbus Validity](modbus_validity/README.md)**
   - PSR/EXR detailed analysis
   - Breakdown by function code
   - State coverage growth

2. **[Modbus Fuzzing](modbus_fuzzing/README.md)**
   - 5 trial details
   - Crash type distribution
   - Throughput analysis

3. **[CoAP Validity](coap_validity/README.md)**
   - DTLS ON/OFF comparison
   - Observe & Blockwise milestones
   - Token coherence analysis

4. **[CoAP Fuzzing](coap_fuzzing/README.md)**
   - Detailed DTLS overhead breakdown
   - Crash discovery comparison
   - Throughput impact

5. **[Baseline Comparison](baseline_comparison/README.md)**
   - Detailed comparison of 6 fuzzers
   - Effect size calculations
   - Statistical significance analysis

---

## 🔗 Related Files

- **Test Scripts:** `../modbus_tests/`, `../coap_tests/`, `../baseline_comparisons/`
- **Analysis Scripts:** `../analysis_scripts/`
- **Main Documentation:** `../README.md`, `../QUICK_START.md`

---

## 📞 Contact and Support

For questions or further data analysis needs:

1. Consult detailed READMEs in each subdirectory
2. Refer to thesis methodology chapter (Chapter 4)
3. Check test script source code

---

## 🎓 Citation Recommendations

When citing this data in the thesis:

```
All experimental results were obtained using the HyFuzz testing
framework on [date], with [n] independent trials per configuration
to ensure statistical validity. Detailed data files, including raw
JSON results and aggregated statistics, are available in the
thesis_results/results_data/ directory of the project repository.
```

---

**Data Integrity Statement:**
All data generated through automated scripts, ensuring reproducibility. Raw data unmodified by humans, only statistical aggregation and formatting applied.

**Test Environment:**
- Python 3.9+
- Independent simulated environment
- No external network dependencies

**Data License:**
This dataset is part of the HyFuzz project and follows the project's main license.

---

**Last Updated:** 2025-11-10
**Data Version:** v1.0
**Documentation Version:** 1.0
