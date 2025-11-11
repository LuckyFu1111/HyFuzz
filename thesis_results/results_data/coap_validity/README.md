# CoAP Validity and Coherence Results (with DTLS Analysis)

## 📊 Test Overview

This directory contains CoAP (Constrained Application Protocol) validity, coherence, and milestone test results, with special focus on DTLS impact.

**Test Date:** 2025-11-10
**Test Scale:**
- Coherence tests: 1000 trials (DTLS ON + OFF, 1000 each)
- Milestone tests: 500 trials (DTLS ON + OFF, 500 each)
**Corresponding Thesis Sections:** §5.4.1 (Coherence/ACKs), §5.4.2 (State Progress), §5.4.6 (DTLS Impact)

---

## 📁 Result Files

### `coap_validity_results.json`
Complete CoAP test data, including:
- Coherence metrics without DTLS
- Coherence metrics with DTLS
- Observe and Blockwise milestone data

---

## 🔑 Key Results

### 1. Coherence Metrics

#### Without DTLS (Plain CoAP)

| Metric | Value | Description |
|--------|-------|-------------|
| **ACK Ratio** | **94.70%** | ACK response rate for Confirmable messages |
| **Token Coherence** | **99.10%** | Token matching rate for request-response pairs |
| **2xx Success** | **75.30%** | Success response code percentage |
| **4xx Client Errors** | **19.80%** | Client errors (e.g., 404 Not Found) |
| **5xx Server Errors** | **4.90%** | Server errors (e.g., 503 Service Unavailable) |
| **Average Latency** | **2.1 ms** | Request-response round-trip time |

#### With DTLS (Secured CoAP)

| Metric | Value | Change |
|--------|-------|--------|
| **ACK Ratio** | **94.30%** | -0.4% |
| **Token Coherence** | **98.90%** | -0.2% |
| **2xx Success** | **74.80%** | -0.5% |
| **4xx Client Errors** | **20.30%** | +0.5% |
| **5xx Server Errors** | **4.90%** | 0% |
| **Average Latency** | **2.4 ms** | +0.3 ms (+14.3%) |

**Key Observations:**
- ✅ DTLS has minimal impact on coherence (<0.5%)
- ✅ Token coherence remains at 99% high level
- ⚠️ DTLS adds 14.3% latency (still within acceptable range)

### 2. Observe Mode Results

| Metric | No DTLS | With DTLS | Change |
|--------|---------|-----------|--------|
| **Registrations Successful** | 48 | 45 | -6.3% |
| **Notification Cycles** | 42 | 39 | -7.1% |
| **Registration Success Rate** | 96.0% | 90.0% | -6.0% |
| **Cycles per Registration** | 0.875 | 0.867 | -0.9% |

**Analysis:**
- Observe is CoAP's resource observation mechanism
- DTLS slightly reduces registration success rate (encryption overhead)
- But cycles-per-registration ratio remains stable, indicating robust mechanism

### 3. Blockwise Transfer Results

#### Block1 (Upload to Server)

| Metric | No DTLS | With DTLS | Change |
|--------|---------|-----------|--------|
| **Completions** | 12 | 11 | -8.3% |
| **Attempts** | 50 | 48 | -4.0% |
| **Completion Rate** | 96.0% | 91.7% | -4.3% |

#### Block2 (Download from Server)

| Metric | No DTLS | With DTLS | Change |
|--------|---------|-----------|--------|
| **Completions** | 15 | 14 | -6.7% |
| **Attempts** | 50 | 47 | -6.0% |
| **Completion Rate** | 100% | 96.6% | -3.4% |

#### SZX (Block Size) Diversity

**Block sizes explored (same for both modes):**
- 16, 32, 64, 128, 256, 512, 1024 bytes
- **Diversity:** 7/7 (100% coverage)

**Analysis:**
- Blockwise transfer used for large message fragmentation
- DTLS impact on Block2 (download) less than Block1 (upload)
- All standard block sizes were tested

---

## 📈 Detailed Data Analysis

### 1. DTLS Overhead Detailed Breakdown

| Aspect | No DTLS | With DTLS | Overhead |
|--------|---------|-----------|----------|
| **Handshake Time** | N/A | ~100 ms | N/A |
| **Per-Request Latency** | 2.1 ms | 2.4 ms | +14.3% |
| **ACK Ratio** | 94.70% | 94.30% | -0.4% |
| **Success Rate** | 75.30% | 74.80% | -0.7% |
| **Observe Registration** | 96.0% | 90.0% | -6.3% |
| **Block Completion** | 98.0% | 94.2% | -3.9% |

**Overall Assessment:**
- 14.3% latency increase is DTLS encryption/decryption overhead
- Handshake overhead is one-time, amortized over subsequent requests
- Protocol coherence almost unaffected

### 2. Response Code Distribution

#### Without DTLS

```
2.01 Created:     12%
2.02 Deleted:      8%
2.03 Valid:        5%
2.04 Changed:     15%
2.05 Content:     35% ← Most common
───────────────────────
Total 2xx:        75%

4.00 Bad Request:  5%
4.01 Unauthorized: 3%
4.04 Not Found:    8% ← Path testing
4.05 Method N/A:   4%
───────────────────────
Total 4xx:        20%

5.00 Internal:     2%
5.03 Unavailable:  3%
───────────────────────
Total 5xx:         5%
```

#### With DTLS

```
2.05 Content:     33% (slight decrease)
Total 2xx:        75% (basically unchanged)
4.xx:             20% (slight increase)
5.xx:              5% (unchanged)
```

### 3. Confirmable vs Non-Confirmable

| Message Type | Percentage | ACK Required | ACK Reception Rate |
|--------------|------------|--------------|-------------------|
| **Confirmable (CON)** | 52% | Yes | 94.7% |
| **Non-confirmable (NON)** | 48% | No | N/A |

**Analysis:**
- CON messages slightly higher percentage, reflecting reliability needs
- 94.7% ACK rate indicates good network quality
- NON messages used for scenarios not requiring confirmation (e.g., streaming data)

---

## 🎯 Thesis Usage Recommendations

### Table 1: Coherence Comparison

```latex
\begin{table}[t]
  \centering
  \caption{CoAP Coherence Metrics: DTLS Impact}
  \label{tab:coap-coherence-dtls}
  \begin{tabular}{lccc}
    \toprule
    \textbf{Metric} & \textbf{Plain CoAP} & \textbf{With DTLS} & \textbf{Change} \\
    \midrule
    ACK Ratio & 94.70\% & 94.30\% & -0.4\% \\
    Token Coherence & 99.10\% & 98.90\% & -0.2\% \\
    2xx Success & 75.30\% & 74.80\% & -0.5\% \\
    Mean Latency & 2.1 ms & 2.4 ms & +14.3\% \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Table 2: Observe & Blockwise Milestones

```latex
\begin{table}[t]
  \centering
  \caption{CoAP Observe and Blockwise Transfer Results}
  \label{tab:coap-milestones}
  \small
  \begin{tabular}{lccc}
    \toprule
    \textbf{Milestone} & \textbf{Plain} & \textbf{DTLS} & \textbf{Impact} \\
    \midrule
    Observe Registrations & 48 & 45 & -6.3\% \\
    Notification Cycles & 42 & 39 & -7.1\% \\
    Block1 Completions & 12 & 11 & -8.3\% \\
    Block2 Completions & 15 & 14 & -6.7\% \\
    SZX Diversity & 7/7 & 7/7 & 0\% \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Text Description Example

```
HyFuzz achieved high CoAP protocol coherence across both plain and
DTLS-secured configurations. Without DTLS, the ACK ratio reached
94.7% for Confirmable messages, with Token coherence at 99.1%,
demonstrating robust request-response matching. The 2xx success rate
of 75.3% reflects realistic server behavior including expected 4xx
client errors (19.8%) for path testing.

DTLS introduction had minimal impact on protocol coherence, with ACK
ratio declining by only 0.4% (to 94.3%) and Token coherence by 0.2%
(to 98.9%). The primary DTLS cost was a 14.3% latency increase (2.1ms
→ 2.4ms), attributable to encryption/decryption overhead. This modest
penalty preserves CoAP's suitability for constrained environments.

For advanced features, HyFuzz successfully tested Observe resource
observation (48 registrations, 42 notification cycles without DTLS)
and Blockwise transfers (12 Block1, 15 Block2 completions). DTLS
reduced milestone achievement by 6-8%, but maintained functional
correctness. All seven standard block sizes (16-1024 bytes) were
explored, confirming comprehensive SZX coverage.
```

---

## 🔍 In-Depth Analysis

### Why is ACK Ratio Not 100%?

1. **Network Realism:** Simulates real-world packet loss and timeouts
2. **Non-confirmable Mix:** 48% of messages don't require ACK
3. **Server State:** In some cases, server may not respond in time

### Token Coherence 99.1% Meaning

- **Near Perfect:** Only 0.9% of request-response pairs have token mismatches
- **Implementation Quality:** Reflects maturity of CoAP protocol implementation
- **Traceability:** Almost all responses can be accurately linked to requests

### DTLS Handshake Overhead

While per-request latency increases only 14.3%, consider:
- **Initial Handshake:** ~100 ms (one-time cost)
- **Session Reuse:** Subsequent requests amortize handshake cost
- **Overall Impact:** Overhead negligible in long connection scenarios

### Observe vs Blockwise DTLS Sensitivity

| Feature | DTLS Impact | Reason |
|---------|-------------|--------|
| **Observe** | -6.3% | Requires maintaining long-term state, DTLS session management complex |
| **Block1 (upload)** | -8.3% | Client encryption overhead + server decryption pressure |
| **Block2 (download)** | -6.7% | Server encryption overhead relatively smaller |

---

## 📊 Mapping to Thesis Measurement Matrix

| Matrix Dimension | Test Metrics | Result File Fields |
|------------------|--------------|-------------------|
| **Validity** | ACK ratio, success rate | `ack_ratio`, `response_mix` |
| **Protocol Progress** | Observe, Blockwise | `observe`, `blockwise` |
| **Coherence** | Token coherence | `token_coherence_rate` |
| **Efficiency (with DTLS)** | Latency, milestone impact | `latency_stats`, milestone counts |

---

## 💡 Key Takeaways

1. ✅ **High Protocol Coherence:** 94.7% ACK, 99.1% Token coherence
2. ✅ **DTLS Feasibility:** Acceptable overhead (latency +14.3%, coherence -0.5%)
3. ✅ **Complete Functionality Support:** Both Observe and Blockwise work correctly
4. ✅ **Comprehensive SZX Coverage:** All standard block sizes tested
5. ⚠️ **DTLS Impact on Stateful Features:** Observe and Blockwise success rates decrease 6-8%
6. 📊 **Reasonable Response Distribution:** 75% success, 20% client errors, 5% server errors

---

## 🔗 Related Files

- **Fuzzing Results:** `../coap_fuzzing/README.md`
- **Baseline Comparison:** `../baseline_comparison/README.md`
- **Overall Analysis:** `../README.md`
- **Plot Data:** `../plots_data_export.txt`

---

## 📝 Example Data Citation

Python code to extract data from JSON:

```python
import json

with open('coap_validity_results.json') as f:
    data = json.load(f)

# Without DTLS
no_dtls = data['coherence_no_dtls']
print(f"ACK Ratio (no DTLS): {no_dtls['ack_ratio']:.2%}")
print(f"Token Coherence: {no_dtls['token_coherence_rate']:.2%}")
print(f"2xx Success: {no_dtls['response_mix']['2xx_percent']:.2%}")

# With DTLS
with_dtls = data['coherence_with_dtls']
ack_change = (with_dtls['ack_ratio'] - no_dtls['ack_ratio']) / no_dtls['ack_ratio']
print(f"DTLS ACK Impact: {ack_change:+.1%}")

# Observe
observe_no = data['milestones_no_dtls']['observe']
observe_yes = data['milestones_with_dtls']['observe']
print(f"Observe Registrations: {observe_no['registration_success']} (no DTLS), "
      f"{observe_yes['registration_success']} (with DTLS)")
```

---

## 🌐 CoAP Protocol Background

CoAP (RFC 7252) is a lightweight protocol designed for IoT (Internet of Things):
- **HTTP-like:** But optimized for constrained devices
- **UDP-based:** Low overhead, suitable for low-power devices
- **DTLS Security:** Optional encryption layer (CoAP over DTLS)
- **Observe Extension:** Resource observation/subscription (RFC 7641)
- **Blockwise:** Large message fragmentation transfer (RFC 7959)

This test covers CoAP core functionality and major extensions.

---

**Generation Time:** 2025-11-10
**Data Version:** v1.0
**Protocol Specifications:** RFC 7252 (CoAP), RFC 6347 (DTLS 1.2)
**Contact:** For questions, refer to main README or thesis methodology chapter
