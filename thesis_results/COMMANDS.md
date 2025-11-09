# Complete Command Reference

## 所有命令速查表 (All Commands Quick Reference)

### 一键运行 (One-Command Run)

```bash
# 运行所有测试 + 分析 + 绘图
cd /home/user/HyFuzz/thesis_results && \
python3 run_all_tests.py && \
python3 analysis_scripts/analyze_results.py && \
python3 analysis_scripts/plot_results.py
```

---

## 分类命令 (Categorized Commands)

### 1. Modbus/TCP 测试

#### 1.1 有效性测试 (Validity Tests)
```bash
# 基本运行
python3 modbus_tests/test_modbus_validity.py

# 自定义试验次数
python3 -c "
import asyncio
from modbus_tests.test_modbus_validity import ModbusValidityTester
from pathlib import Path
async def run():
    tester = ModbusValidityTester(Path('results_data/modbus_validity'))
    await tester.run_all_tests(num_trials=2000)  # 自定义为 2000
asyncio.run(run())
"
```

**输出文件:**
- `results_data/modbus_validity/modbus_validity_results.json`
- `results_data/modbus_validity/modbus_state_progress.json`

**关键指标:**
- `PSR` - Protocol Success Rate
- `EXR` - Exception Rate
- `per_function_code` - 每个功能码的详细数据
- `unique_states` - 发现的唯一状态数
- `fc_address_coverage` - FC×地址覆盖

#### 1.2 模糊测试 (Fuzzing Tests)
```bash
# 基本运行
python3 modbus_tests/test_modbus_fuzzing.py

# 自定义参数
python3 -c "
import asyncio
from modbus_tests.test_modbus_fuzzing import ModbusFuzzingTester
from pathlib import Path
async def run():
    tester = ModbusFuzzingTester(Path('results_data/modbus_fuzzing'))
    await tester.multi_trial_campaign(
        num_trials=10,           # 10 次试验
        duration_per_trial=120   # 每次 120 秒
    )
asyncio.run(run())
"
```

**输出文件:**
- `results_data/modbus_fuzzing/modbus_fuzzing_results.json`

**关键指标:**
- `aggregate.execs.mean` - 平均执行次数
- `aggregate.unique_crashes.mean` - 平均唯一崩溃数
- `aggregate.throughput_exec_per_sec.mean` - 平均吞吐量

---

### 2. CoAP 测试

#### 2.1 有效性和一致性测试 (Validity & Coherence)
```bash
# 基本运行 (测试 DTLS ON 和 OFF)
python3 coap_tests/test_coap_validity.py

# 仅测试无 DTLS
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

# 仅测试 Observe & Blockwise
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

**输出文件:**
- `results_data/coap_validity/coap_validity_results.json`

**关键指标:**
- `ack_ratio` - ACK 比率
- `token_coherence_rate` - Token 一致性
- `response_mix` - 响应码分布 (2xx/4xx/5xx)
- `observe.registration_success` - Observe 注册成功数
- `blockwise.block1_completions` - Block1 完成数

#### 2.2 模糊测试和 DTLS 对比
```bash
# 基本运行
python3 coap_tests/test_coap_fuzzing.py

# 单独运行 DTLS 影响对比
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

**输出文件:**
- `results_data/coap_fuzzing/coap_fuzzing_results.json`

**关键指标:**
- `comparison.dtls_overhead_percent` - DTLS 开销百分比
- `no_dtls_trials` - 无 DTLS 试验结果
- `with_dtls_trials` - 有 DTLS 试验结果

---

### 3. 基线对比 (Baseline Comparison)

```bash
# 基本运行 (对比所有模糊器)
python3 baseline_comparisons/compare_baselines.py

# 仅对比 Modbus
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

# 仅对比 CoAP
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

**输出文件:**
- `results_data/baseline_comparison/baseline_comparison_results.json`

**对比的模糊器:**
- AFL (基线)
- AFL++
- AFLNet (协议感知)
- libFuzzer
- Grammar-based
- HyFuzz

**关键指标:**
- `effect_sizes.unique_crashes.improvement_percent` - 崩溃发现改进
- `effect_sizes.coverage.improvement_percent` - 覆盖率改进
- `fuzzer_rankings` - 模糊器排名

---

### 4. 结果分析 (Analysis)

#### 4.1 数据分析
```bash
# 完整分析
python3 analysis_scripts/analyze_results.py

# 查看汇总
cat results_data/summary.txt

# 查看 JSON 数据
cat results_data/analysis_summary.json | python3 -m json.tool

# 提取特定指标
python3 -c "
import json
with open('results_data/analysis_summary.json') as f:
    data = json.load(f)
    print('Modbus PSR:', data['modbus']['validity']['PSR'])
    print('CoAP ACK Ratio (no DTLS):', data['coap']['coherence_no_dtls']['ack_ratio'])
"
```

**输出文件:**
- `results_data/analysis_summary.json` - 结构化分析
- `results_data/summary.txt` - 文本汇总

#### 4.2 生成图表
```bash
# 生成所有图表
python3 analysis_scripts/plot_results.py

# 查看生成的图表
ls -lh plots/

# 在 LaTeX 中使用
echo "\\includegraphics[width=0.9\\linewidth]{plots/modbus_psr_exr.png}"
```

**生成的图表 (300 DPI):**
1. `modbus_psr_exr.png` - Modbus PSR vs EXR
2. `modbus_state_coverage.png` - 状态覆盖增长
3. `coap_coherence_dtls.png` - CoAP 一致性 (DTLS 影响)
4. `baseline_comparison_modbus.png` - Modbus 基线对比
5. `baseline_comparison_coap.png` - CoAP 基线对比
6. `fuzzing_efficiency.png` - 模糊测试效率

---

### 5. 批处理命令 (Batch Commands)

#### 5.1 运行所有 Modbus 测试
```bash
python3 modbus_tests/test_modbus_validity.py && \
python3 modbus_tests/test_modbus_fuzzing.py
```

#### 5.2 运行所有 CoAP 测试
```bash
python3 coap_tests/test_coap_validity.py && \
python3 coap_tests/test_coap_fuzzing.py
```

#### 5.3 完整流程 (测试 + 分析 + 绘图)
```bash
# 完整运行
cd /home/user/HyFuzz/thesis_results

# 步骤 1: 所有测试
python3 run_all_tests.py

# 步骤 2: 分析
python3 analysis_scripts/analyze_results.py

# 步骤 3: 绘图
python3 analysis_scripts/plot_results.py

# 步骤 4: 查看结果
cat results_data/summary.txt
ls plots/
```

---

### 6. 数据查询命令 (Data Query)

#### 6.1 Modbus 数据查询
```bash
# 查询 PSR
python3 -c "
import json
with open('results_data/modbus_validity/modbus_validity_results.json') as f:
    data = json.load(f)
    print(f'PSR: {data[\"PSR\"]:.2%}')
    print(f'EXR: {data[\"EXR\"]:.2%}')
"

# 查询唯一状态数
python3 -c "
import json
with open('results_data/modbus_validity/modbus_state_progress.json') as f:
    data = json.load(f)
    print(f'Unique States: {data[\"unique_states\"]}')
"

# 查询平均崩溃数
python3 -c "
import json
with open('results_data/modbus_fuzzing/modbus_fuzzing_results.json') as f:
    data = json.load(f)
    print(f'Mean Crashes: {data[\"aggregate\"][\"unique_crashes\"][\"mean\"]:.1f}')
"
```

#### 6.2 CoAP 数据查询
```bash
# 查询 ACK 比率
python3 -c "
import json
with open('results_data/coap_validity/coap_validity_results.json') as f:
    data = json.load(f)
    print(f'ACK Ratio (no DTLS): {data[\"coherence_no_dtls\"][\"ack_ratio\"]:.2%}')
    print(f'ACK Ratio (with DTLS): {data[\"coherence_with_dtls\"][\"ack_ratio\"]:.2%}')
"

# 查询 DTLS 开销
python3 -c "
import json
with open('results_data/coap_fuzzing/coap_fuzzing_results.json') as f:
    data = json.load(f)
    print(f'DTLS Overhead: {data[\"comparison\"][\"dtls_overhead_percent\"]:.1f}%')
"
```

#### 6.3 基线对比查询
```bash
# 查询改进百分比
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

### 7. 清理命令 (Cleanup)

```bash
# 清理所有结果
rm -rf results_data/* plots/*

# 仅清理图表
rm -rf plots/*

# 仅清理特定测试结果
rm -rf results_data/modbus_validity/*
rm -rf results_data/coap_fuzzing/*
```

---

### 8. 调试命令 (Debugging)

```bash
# 检查目录结构
tree thesis_results/ -L 2

# 检查脚本语法
python3 -m py_compile modbus_tests/test_modbus_validity.py
python3 -m py_compile coap_tests/test_coap_validity.py

# 测试单个函数
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

### 9. 性能监控 (Performance Monitoring)

```bash
# 监控执行时间
time python3 run_all_tests.py

# 监控单个测试
time python3 modbus_tests/test_modbus_validity.py

# 监控内存使用
/usr/bin/time -v python3 run_all_tests.py
```

---

### 10. 生成论文表格 (Generate Thesis Tables)

```bash
# 生成 LaTeX 表格数据
python3 -c "
import json

# 加载分析数据
with open('results_data/analysis_summary.json') as f:
    data = json.load(f)

# Modbus 表格
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

## 常见工作流 (Common Workflows)

### 工作流 1: 快速测试
```bash
# 快速验证 (减少试验次数)
cd /home/user/HyFuzz/thesis_results
python3 -c "
import asyncio
from modbus_tests.test_modbus_validity import ModbusValidityTester
from pathlib import Path
async def quick_test():
    tester = ModbusValidityTester(Path('results_data/quick_test'))
    await tester.run_all_tests(num_trials=100)  # 仅 100 次
asyncio.run(quick_test())
"
```

### 工作流 2: 完整论文数据收集
```bash
# 按顺序运行所有测试
cd /home/user/HyFuzz/thesis_results
python3 run_all_tests.py
python3 analysis_scripts/analyze_results.py
python3 analysis_scripts/plot_results.py

# 检查结果
cat results_data/summary.txt
ls -lh plots/
```

### 工作流 3: 仅更新图表
```bash
# 如果已有数据，仅重新生成图表
cd /home/user/HyFuzz/thesis_results
python3 analysis_scripts/plot_results.py
```

---

## 环境准备 (Environment Setup)

```bash
# 安装依赖 (如需绘图)
pip3 install matplotlib numpy seaborn

# 检查 Python 版本
python3 --version  # 需要 3.9+

# 检查磁盘空间
df -h /home/user/HyFuzz/thesis_results/
```

---

## 故障排除命令 (Troubleshooting)

```bash
# 问题 1: 导入错误
cd /home/user/HyFuzz/thesis_results
export PYTHONPATH="/home/user/HyFuzz/HyFuzz-Ubuntu-Client/src:$PYTHONPATH"

# 问题 2: 权限错误
chmod -R 755 /home/user/HyFuzz/thesis_results/
chmod +x *.py */*.py

# 问题 3: 结果目录不存在
mkdir -p results_data/{modbus_validity,modbus_fuzzing,coap_validity,coap_fuzzing,baseline_comparison}
mkdir -p plots/
```

---

**提示:** 将常用命令添加到 shell 别名:

```bash
# 添加到 ~/.bashrc
alias thesis-test='cd /home/user/HyFuzz/thesis_results && python3 run_all_tests.py'
alias thesis-analyze='cd /home/user/HyFuzz/thesis_results && python3 analysis_scripts/analyze_results.py'
alias thesis-plot='cd /home/user/HyFuzz/thesis_results && python3 analysis_scripts/plot_results.py'
alias thesis-summary='cat /home/user/HyFuzz/thesis_results/results_data/summary.txt'
```
