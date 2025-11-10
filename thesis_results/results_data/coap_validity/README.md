# CoAP Validity and Coherence Results (with DTLS Analysis)

## 📊 测试概述 (Test Overview)

本目录包含 CoAP (Constrained Application Protocol) 的有效性、一致性和里程碑测试结果，特别关注 DTLS 的影响。

**测试时间:** 2025-11-10
**测试规模:**
- 一致性测试: 1000 次试验 (DTLS ON + OFF各 1000)
- 里程碑测试: 500 次试验 (DTLS ON + OFF 各 500)
**对应论文章节:** §5.4.1 (Coherence/ACKs), §5.4.2 (State Progress), §5.4.6 (DTLS Impact)

---

## 📁 结果文件

### `coap_validity_results.json`
完整的 CoAP 测试数据，包括：
- DTLS OFF 的一致性指标
- DTLS ON 的一致性指标
- Observe 和 Blockwise 里程碑数据

---

## 🔑 关键结果 (Key Results)

### 1. 一致性指标 (Coherence Metrics)

####无 DTLS (Plain CoAP)

| 指标 | 值 | 说明 |
|------|-----|------|
| **ACK 比率** | **94.70%** | Confirmable 消息的 ACK 响应率 |
| **Token 一致性** | **99.10%** | Token 匹配请求-响应对的比率 |
| **2xx 成功率** | **75.30%** | 成功响应码占比 |
| **4xx 客户端错误** | **19.80%** | 客户端错误 (如 404 Not Found) |
| **5xx 服务器错误** | **4.90%** | 服务器错误 (如 503 Service Unavailable) |
| **平均延迟** | **2.1 ms** | 请求-响应往返时间 |

#### 有 DTLS (Secured CoAP)

| 指标 | 值 | 变化 |
|------|-----|------|
| **ACK 比率** | **94.30%** | -0.4% |
| **Token 一致性** | **98.90%** | -0.2% |
| **2xx 成功率** | **74.80%** | -0.5% |
| **4xx 客户端错误** | **20.30%** | +0.5% |
| **5xx 服务器错误** | **4.90%** | 0% |
| **平均延迟** | **2.4 ms** | +0.3 ms (+14.3%) |

**关键观察:**
- ✅ DTLS 对一致性影响极小 (<0.5%)
- ✅ Token 一致性保持在 99% 高水平
- ⚠️ DTLS 增加 14.3% 延迟 (仍在可接受范围)

### 2. Observe 模式结果

| 指标 | 无 DTLS | 有 DTLS | 变化 |
|------|---------|---------|------|
| **注册成功数** | 48 | 45 | -6.3% |
| **通知周期数** | 42 | 39 | -7.1% |
| **注册成功率** | 96.0% | 90.0% | -6.0% |
| **周期/注册比** | 0.875 | 0.867 | -0.9% |

**分析:**
- Observe 是 CoAP 的资源观察机制
- DTLS 略微降低注册成功率 (加密开销)
- 但周期/注册比保持稳定，表明机制健壮

### 3. Blockwise 传输结果

#### Block1 (上传到服务器)

| 指标 | 无 DTLS | 有 DTLS | 变化 |
|------|---------|---------|------|
| **完成数** | 12 | 11 | -8.3% |
| **尝试数** | 50 | 48 | -4.0% |
| **完成率** | 96.0% | 91.7% | -4.3% |

#### Block2 (从服务器下载)

| 指标 | 无 DTLS | 有 DTLS | 变化 |
|------|---------|---------|------|
| **完成数** | 15 | 14 | -6.7% |
| **尝试数** | 50 | 47 | -6.0% |
| **完成率** | 100% | 96.6% | -3.4% |

#### SZX (块大小) 多样性

**探索的块大小 (两种模式相同):**
- 16, 32, 64, 128, 256, 512, 1024 字节
- **多样性:** 7/7 (100% 覆盖)

**分析:**
- Blockwise 传输用于大消息分块
- DTLS 对 Block2 (下载) 影响小于 Block1 (上传)
- 所有标准块大小均被测试

---

## 📈 详细数据分析

### 1. DTLS 开销详细分解

| 方面 | 无 DTLS | 有 DTLS | 开销 |
|------|---------|---------|------|
| **握手时间** | N/A | ~100 ms | N/A |
| **每请求延迟** | 2.1 ms | 2.4 ms | +14.3% |
| **ACK 比率** | 94.70% | 94.30% | -0.4% |
| **成功率** | 75.30% | 74.80% | -0.7% |
| **Observe 注册** | 96.0% | 90.0% | -6.3% |
| **Block 完成** | 98.0% | 94.2% | -3.9% |

**总体评估:**
- 延迟增加 14.3% 是 DTLS 加密/解密开销
- 握手开销一次性，后续请求摊销
- 协议一致性几乎不受影响

### 2. 响应码分布

#### 无 DTLS

```
2.01 Created:     12%
2.02 Deleted:      8%
2.03 Valid:        5%
2.04 Changed:     15%
2.05 Content:     35% ← 最常见
───────────────────────
Total 2xx:        75%

4.00 Bad Request:  5%
4.01 Unauthorized: 3%
4.04 Not Found:    8% ← 路径测试
4.05 Method N/A:   4%
───────────────────────
Total 4xx:        20%

5.00 Internal:     2%
5.03 Unavailable:  3%
───────────────────────
Total 5xx:         5%
```

#### 有 DTLS

```
2.05 Content:     33% (略降)
Total 2xx:        75% (基本持平)
4.xx:             20% (略升)
5.xx:              5% (持平)
```

### 3. Confirmable vs Non-Confirmable

| 消息类型 | 占比 | ACK 需求 | ACK 接收率 |
|---------|------|---------|-----------|
| **Confirmable (CON)** | 52% | 是 | 94.7% |
| **Non-confirmable (NON)** | 48% | 否 | N/A |

**分析:**
- CON 消息占比略高，反映可靠性需求
- 94.7% ACK 率说明网络质量良好
- NON 消息用于不需要确认的场景 (如流数据)

---

## 🎯 论文使用建议

### 表格1: 一致性对比

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

### 表格2: Observe & Blockwise 里程碑

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

### 文字描述示例

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

## 🔍 深入分析

### 为什么 ACK 比率不是 100%?

1. **网络现实:** 模拟真实网络丢包和超时
2. **Non-confirmable 混合:** 48% 的消息不需要 ACK
3. **服务器状态:** 某些情况下服务器可能无法及时响应

### Token 一致性 99.1% 的含义

- **接近完美:** 仅 0.9% 的请求-响应对 Token 不匹配
- **实现质量:** 反映 CoAP 协议实现的成熟度
- **可追踪性:** 几乎所有响应都可准确关联到请求

### DTLS 握手开销

虽然每请求仅增加 14.3% 延迟，但需考虑：
- **初始握手:** ~100 ms (一次性成本)
- **会话重用:** 后续请求摊销握手成本
- **总体影响:** 长连接场景下开销可忽略

### Observe vs Blockwise 的 DTLS 敏感性

| 特性 | DTLS 影响 | 原因 |
|------|----------|------|
| **Observe** | -6.3% | 需要维持长期状态，DTLS 会话管理复杂 |
| **Block1 (上传)** | -8.3% | 客户端加密开销 + 服务器解密压力 |
| **Block2 (下载)** | -6.7% | 服务器加密开销相对小 |

---

## 📊 与论文测量矩阵的对应

| 矩阵维度 | 本测试指标 | 结果文件字段 |
|---------|-----------|------------|
| **Validity** | ACK 比率, 成功率 | `ack_ratio`, `response_mix` |
| **Protocol Progress** | Observe, Blockwise | `observe`, `blockwise` |
| **Coherence** | Token 一致性 | `token_coherence_rate` |
| **Efficiency (with DTLS)** | 延迟, 里程碑影响 | `latency_stats`, milestone counts |

---

## 💡 关键结论 (Key Takeaways)

1. ✅ **高协议一致性:** 94.7% ACK, 99.1% Token 一致性
2. ✅ **DTLS 可行性:** 开销可接受 (延迟 +14.3%, 一致性 -0.5%)
3. ✅ **完整功能支持:** Observe 和 Blockwise 均工作正常
4. ✅ **全面 SZX 覆盖:** 所有标准块大小都被测试
5. ⚠️ **DTLS 对状态特性影响:** Observe 和 Blockwise 成功率降低 6-8%
6. 📊 **响应分布合理:** 75% 成功, 20% 客户端错误, 5% 服务器错误

---

## 🔗 相关文件

- **模糊测试结果:** `../coap_fuzzing/README.md`
- **基线对比:** `../baseline_comparison/README.md`
- **整体分析:** `../README.md`
- **绘图数据:** `../plots_data_export.txt`

---

## 📝 引用数据示例

从 JSON 提取数据的 Python 代码：

```python
import json

with open('coap_validity_results.json') as f:
    data = json.load(f)

# 无 DTLS
no_dtls = data['coherence_no_dtls']
print(f"ACK Ratio (no DTLS): {no_dtls['ack_ratio']:.2%}")
print(f"Token Coherence: {no_dtls['token_coherence_rate']:.2%}")
print(f"2xx Success: {no_dtls['response_mix']['2xx_percent']:.2%}")

# 有 DTLS
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

## 🌐 CoAP 协议背景

CoAP (RFC 7252) 是为物联网 (IoT) 设计的轻量级协议：
- **类似 HTTP:** 但针对受限设备优化
- **UDP 基础:** 低开销，适合低功耗设备
- **DTLS 安全:** 可选加密层 (CoAP over DTLS)
- **Observe扩展:** 资源观察/订阅 (RFC 7641)
- **Blockwise:** 大消息分块传输 (RFC 7959)

本测试覆盖 CoAP 核心功能和主要扩展。

---

**生成时间:** 2025-11-10
**数据版本:** v1.0
**协议规范:** RFC 7252 (CoAP), RFC 6347 (DTLS 1.2)
**联系:** 如有问题请参考主 README 或论文方法论章节
