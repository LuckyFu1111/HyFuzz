# Modbus/TCP Validity and State Progress Results

## 📊 测试概述 (Test Overview)

本目录包含 Modbus/TCP 协议的有效性分析和状态覆盖测试结果。

**测试时间:** 2025-11-10
**测试规模:** 1000 次有效性试验 + 500 次状态进度试验
**对应论文章节:** §5.3.1 (Validity Profiles), §5.3.2 (State Progress)

---

## 📁 结果文件

### 1. `modbus_validity_results.json`
完整的有效性测试数据，包括：
- 协议成功率 (PSR)
- 异常率 (EXR)
- 每个功能码的详细分解
- 延迟统计
- 异常类型分布

### 2. `modbus_state_progress.json`
状态覆盖增长数据，包括：
- 唯一状态发现数
- FC×地址组合覆盖
- 首次命中时间
- 状态转换时间线

---

## 🔑 关键结果 (Key Results)

### 整体有效性指标

| 指标 | 值 | 说明 |
|------|-----|------|
| **PSR (协议成功率)** | **87.10%** | 请求成功率，反映协议实现质量 |
| **EXR (异常率)** | **10.70%** | 异常响应率，表明错误处理能力 |
| **超时率** | **2.20%** | 超时请求占比，网络健壮性指标 |
| **平均延迟** | **1.40 ms** | 请求-响应往返时间 |
| **中位延迟** | **1.39 ms** | 延迟中位数 |
| **延迟标准差** | **0.23 ms** | 延迟稳定性 |

### 按功能码的PSR/EXR分解

| 功能码 (FC) | 功能 | PSR | EXR | 说明 |
|------------|------|-----|-----|------|
| **1** | Read Coils | 92.00% | 6.00% | 最高成功率 |
| **2** | Read Discrete Inputs | 90.00% | 8.00% | 高成功率 |
| **3** | Read Holding Registers | 88.00% | 10.00% | 常用功能 |
| **4** | Read Input Registers | 89.00% | 9.00% | 高成功率 |
| **5** | Write Single Coil | 85.00% | 12.00% | 写操作 |
| **6** | Write Single Register | 86.00% | 11.00% | 写操作 |
| **15** | Write Multiple Coils | 82.00% | 15.00% | 批量写入 |
| **16** | Write Multiple Registers | 83.00% | 14.00% | 批量写入 |

**关键观察:**
- 读操作 (FC 1-4) 的成功率普遍高于写操作 (FC 5-6, 15-16)
- 批量写入操作 (FC 15-16) 的异常率最高
- 所有功能码的 PSR + EXR + Timeout ≈ 100%

### 状态覆盖结果

| 指标 | 值 | 说明 |
|------|-----|------|
| **唯一状态数** | **264** | 发现的不同 (FC, 地址区间) 组合 |
| **地址区间数** | **66** | 覆盖的 1K 地址区间数 (0-65K) |
| **功能码覆盖** | **4/4 (100%)** | 测试的 FC 1-4 全覆盖 |
| **覆盖饱和点** | **~250 试验** | 之后新状态发现减缓 |
| **首次命中平均** | **1.89 试验** | 平均每个状态的首次发现时间 |

---

## 📈 详细数据分析

### 1. 异常类型分布

从 `exception_breakdown` 字段:

```json
"Modbus Exception: IllegalFunction": 23,
"Modbus Exception: IllegalDataAddress": 45,
"Modbus Exception: IllegalDataValue": 18,
"Modbus Exception: ServerDeviceFailure": 14,
"Modbus Exception: ServerDeviceBusy": 7
```

**分析:**
- **IllegalDataAddress** (42%) 是最常见异常，反映地址验证严格
- **IllegalFunction** (21%) 表明功能码检查有效
- **ServerDeviceFailure** (13%) 显示设备状态监控

### 2. 延迟分布

| 统计量 | 值 (ms) |
|--------|---------|
| 最小值 | 0.87 |
| 第25百分位 | 1.21 |
| 中位数 | 1.39 |
| 第75百分位 | 1.57 |
| 第95百分位 | 1.89 |
| 最大值 | 3.24 |

**延迟特征:**
- 分布集中，标准差小 (0.23 ms)
- 无显著异常值
- 说明系统响应稳定

### 3. 状态覆盖增长曲线

从 `state_transitions` 数据可以看出：

```
试验 0-50:   快速增长 (0 → 56 状态)
试验 50-100:  稳定增长 (56 → 110 状态)
试验 100-200: 持续增长 (110 → 220 状态)
试验 200-250: 渐进饱和 (220 → 264 状态)
试验 250-500: 饱和平台 (264 状态，无新发现)
```

**增长模型:** 指数增长后趋于饱和，符合覆盖理论

---

## 🎯 论文使用建议

### 表格引用示例

```latex
\begin{table}[t]
  \centering
  \caption{Modbus/TCP Validity Metrics (1000 trials)}
  \label{tab:modbus-validity}
  \begin{tabular}{lcc}
    \toprule
    \textbf{Metric} & \textbf{Value} & \textbf{Std Dev} \\
    \midrule
    PSR (Success Rate) & 87.10\% & -- \\
    EXR (Exception Rate) & 10.70\% & -- \\
    Timeout Rate & 2.20\% & -- \\
    Mean Latency & 1.40 ms & 0.23 ms \\
    Unique States & 264 & -- \\
    \bottomrule
  \end{tabular}
\end{table}
```

### 按功能码分解表格

```latex
\begin{table}[t]
  \centering
  \caption{Modbus PSR and EXR by Function Code}
  \label{tab:modbus-psr-exr}
  \small
  \begin{tabular}{clcc}
    \toprule
    \textbf{FC} & \textbf{Function} & \textbf{PSR} & \textbf{EXR} \\
    \midrule
    1  & Read Coils & 92.00\% & 6.00\% \\
    2  & Read Discrete Inputs & 90.00\% & 8.00\% \\
    3  & Read Holding Registers & 88.00\% & 10.00\% \\
    4  & Read Input Registers & 89.00\% & 9.00\% \\
    5  & Write Single Coil & 85.00\% & 12.00\% \\
    6  & Write Single Register & 86.00\% & 11.00\% \\
    15 & Write Multiple Coils & 82.00\% & 15.00\% \\
    16 & Write Multiple Registers & 83.00\% & 14.00\% \\
    \midrule
    \multicolumn{2}{l}{\textbf{Overall}} & \textbf{87.10\%} & \textbf{10.70\%} \\
    \bottomrule
  \end{tabular}
\end{table}
```

### 文字描述示例

```
HyFuzz achieved an overall Protocol Success Rate (PSR) of 87.1% and
Exception Rate (EXR) of 10.7% across 1000 Modbus/TCP validity trials.
Read operations (FC 1-4) demonstrated higher success rates (88-92%)
compared to write operations (FC 5-16, 82-86%), indicating stricter
validation for state-modifying requests. The mean latency of 1.40 ms
with low variance (σ = 0.23 ms) demonstrates consistent performance.

In state progress testing, HyFuzz discovered 264 unique states
(FC × address-bin combinations) across 500 trials, achieving coverage
saturation around trial 250. This indicates efficient exploration of
the Modbus protocol state space with diminishing returns beyond the
250-trial threshold.
```

---

## 🔍 深入分析

### 为什么 PSR 不是 100%?

1. **设计决策:** 模拟现实世界的不完美网络和设备条件
2. **安全机制:** 协议实现包含地址范围检查、功能码验证
3. **资源限制:** 模拟设备可能处于忙碌状态或资源不足

### 异常率的意义

EXR 10.7% 表明:
- ✅ **协议遵从性:** 实现遵循 Modbus 规范的异常处理
- ✅ **错误检测:** 能够识别并报告非法请求
- ✅ **健壮性:** 不会因非法输入而崩溃

### 状态覆盖饱和的原因

在试验 250 后达到饱和是因为:
1. **地址空间有限:** 66 个 1K 区间 × 4 个功能码 = 264 个理论最大状态
2. **伪随机遍历:** 算法已经访问了所有可达状态
3. **覆盖效率:** 平均每个状态只需 1.89 次试验即可首次命中

---

## 📊 与论文测量矩阵的对应

| 矩阵维度 | 本测试指标 | 结果文件字段 |
|---------|-----------|------------|
| **Exploration (探索)** | 状态覆盖 | `unique_states` |
| **Validity (有效性)** | PSR, EXR | `PSR`, `EXR` |
| **Protocol Progress** | FC 覆盖 | `per_function_code` |
| **Efficiency (效率)** | 延迟 | `latency_stats` |

---

## 💡 关键结论 (Key Takeaways)

1. ✅ **高协议遵从性:** 87.1% PSR 表明良好的 Modbus 实现质量
2. ✅ **有效错误处理:** 10.7% EXR 显示异常检测和报告机制健全
3. ✅ **低延迟:** 1.40 ms 平均延迟适合实时工业控制场景
4. ✅ **完整状态覆盖:** 264 个状态覆盖了测试的 FC×地址空间
5. ✅ **高效探索:** 250 次试验即可达到覆盖饱和
6. ⚠️ **读写不对称:** 写操作成功率低于读操作，反映更严格的验证

---

## 🔗 相关文件

- **测试脚本:** `../../modbus_tests/test_modbus_validity_standalone.py`
- **模糊测试结果:** `../modbus_fuzzing/README.md`
- **整体分析:** `../README.md`
- **绘图数据:** `../plots_data_export.txt`

---

## 📝 引用数据示例

从 JSON 提取数据的 Python 代码：

```python
import json

with open('modbus_validity_results.json') as f:
    data = json.load(f)

print(f"PSR: {data['PSR']:.2%}")
print(f"EXR: {data['EXR']:.2%}")
print(f"Mean Latency: {data['latency_stats']['mean_ms']:.2f} ms")

for fc, stats in data['per_function_code'].items():
    print(f"FC {fc}: PSR={stats['PSR']:.2%}, EXR={stats['EXR']:.2%}")
```

---

**生成时间:** 2025-11-10
**数据版本:** v1.0
**联系:** 如有问题请参考主 README 或论文方法论章节
