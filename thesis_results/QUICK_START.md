# Thesis Results - Quick Start Guide

## 快速开始指南 (Quick Start)

### 一键运行所有测试 (Run All Tests)

```bash
cd /home/user/HyFuzz/thesis_results

# 运行所有测试 (约15-20分钟)
python3 run_all_tests.py

# 分析结果
python3 analysis_scripts/analyze_results.py

# 生成图表
python3 analysis_scripts/plot_results.py
```

### 分步运行 (Step by Step)

#### 1. Modbus/TCP 测试

```bash
# 测试有效性和异常分析
python3 modbus_tests/test_modbus_validity.py

# 测试模糊测试性能
python3 modbus_tests/test_modbus_fuzzing.py
```

**输出位置:** `results_data/modbus_validity/` 和 `results_data/modbus_fuzzing/`

**测试指标:**
- PSR (协议成功率)
- EXR (异常率)
- 状态覆盖 (FC × 地址 × unit-id)
- 崩溃发现
- 吞吐量 (exec/s)

#### 2. CoAP 测试 (包含 DTLS)

```bash
# 测试一致性、ACK、响应混合
python3 coap_tests/test_coap_validity.py

# 测试模糊测试 (DTLS 对比)
python3 coap_tests/test_coap_fuzzing.py
```

**输出位置:** `results_data/coap_validity/` 和 `results_data/coap_fuzzing/`

**测试指标:**
- MID/Token 一致性
- ACK 比率
- 响应码分布 (2xx/4xx/5xx)
- Observe 注册/通知周期
- Blockwise 传输完成
- DTLS 开销分析

#### 3. 基线对比

```bash
# 对比 HyFuzz vs AFL/AFL++/AFLNet/libFuzzer/Grammar
python3 baseline_comparisons/compare_baselines.py
```

**输出位置:** `results_data/baseline_comparison/`

**对比内容:**
- 漏洞发现能力
- 代码覆盖率
- 执行吞吐量
- 效果大小和置信区间

#### 4. 结果分析和可视化

```bash
# 步骤 1: 分析所有结果
python3 analysis_scripts/analyze_results.py
# 输出: results_data/analysis_summary.json
#      results_data/summary.txt

# 步骤 2: 生成图表 (300 DPI 高质量)
python3 analysis_scripts/plot_results.py
# 输出: plots/*.png
```

## 主要测试内容对应论文章节

### 对应 Chapter Results 的测试:

| 论文章节 | 测试脚本 | 输出文件 |
|---------|---------|---------|
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

## 生成的图表

运行 `plot_results.py` 后会生成以下图表:

1. **modbus_psr_exr.png** - Modbus PSR vs EXR (按功能码)
2. **modbus_state_coverage.png** - Modbus 状态覆盖增长
3. **coap_coherence_dtls.png** - CoAP 一致性指标 (DTLS 影响)
4. **baseline_comparison_modbus.png** - Modbus 基线对比
5. **baseline_comparison_coap.png** - CoAP 基线对比
6. **fuzzing_efficiency.png** - 模糊测试效率

所有图表为 300 DPI，可直接用于论文。

## 预期运行时间

| 测试 | 预计时间 |
|-----|---------|
| Modbus Validity | 2-3 分钟 |
| Modbus Fuzzing | 5 分钟 |
| CoAP Validity | 3-4 分钟 |
| CoAP Fuzzing | 6 分钟 |
| Baseline Comparison | 10-12 分钟 |
| **总计** | **~15-20 分钟** |

## 检查结果

```bash
# 查看结果目录
ls -R results_data/

# 查看汇总
cat results_data/summary.txt

# 查看生成的图表
ls plots/
```

## 在论文中使用结果

### 表格数据

结果文件 `results_data/summary.txt` 包含可直接引用的数据:

```
PSR: 85.2%
EXR: 12.3%
Mean Latency: 3.45 ms
...
```

### 图表引用

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\linewidth]{plots/modbus_psr_exr.png}
  \caption{Modbus Protocol Success vs Exception Rate by Function Code}
  \label{fig:modbus-psr-exr}
\end{figure}
```

## 自定义参数

如需修改测试参数，编辑各脚本的 `main()` 函数:

```python
# 例如: 增加试验次数
await tester.run_all_tests(num_trials=2000)  # 默认 1000

# 例如: 延长模糊测试时间
await tester.multi_trial_campaign(num_trials=10, duration_per_trial=120)  # 默认 5, 60
```

## 故障排除

### 1. 导入错误
```bash
# 确保在正确目录运行
cd /home/user/HyFuzz/thesis_results
```

### 2. 缺少依赖
```bash
# 安装绘图库 (仅绘图需要)
pip3 install matplotlib numpy seaborn
```

### 3. 权限问题
```bash
# 确保结果目录可写
chmod -R 755 results_data/ plots/
```

## 需要帮助?

详细文档请参考: `README.md`
