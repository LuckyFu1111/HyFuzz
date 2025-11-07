# HyFuzz GUI 快速入门指南

## 5 分钟快速上手

### 第一步：安装依赖（仅首次）

#### Windows 系统
```powershell
# 打开 PowerShell 或 命令提示符
cd C:\path\to\HyFuzz\ui
pip install -r requirements.txt
```

#### Ubuntu 系统
```bash
# 打开终端
cd /path/to/HyFuzz/ui

# 安装 tkinter（如果尚未安装）
sudo apt-get update
sudo apt-get install python3-tk

# 安装 Python 依赖
pip install -r requirements.txt
```

### 第二步：启动 HyFuzz 服务器

**选择适合你的系统：**

#### Windows（控制平面）
```bash
cd HyFuzz-Windows-Server
python scripts/start_server.py
```

服务器将在 `http://localhost:8080` 启动

#### Ubuntu（执行客户端）
```bash
cd HyFuzz-Ubuntu-Client
python scripts/start_client.py --server-url http://YOUR_WINDOWS_IP:8080
```

### 第三步：启动 GUI

```bash
# 从 HyFuzz 根目录运行
cd /path/to/HyFuzz
python ui/launch_gui.py
```

或者使用帮助命令查看更多选项：
```bash
python ui/launch_gui.py --help
```

### 第四步：创建第一个模糊测试活动

1. **打开 GUI** 后，你会看到多个标签页
2. **在 "活动管理" 标签页**：
   - 输入活动名称，例如：`我的第一个测试`
   - 选择协议，例如：`coap`
   - 输入目标地址，例如：`localhost:5683`
   - 设置 Payload 数量，例如：`10`
   - 点击 **创建活动** 按钮

3. **在活动列表中**：
   - 选择刚创建的活动
   - 点击 **启动** 按钮

4. **切换到 "实时监控" 标签页**：
   - 点击 **开始监控** 按钮
   - 观察进度条和实时日志

5. **查看结果**：
   - 切换到 **执行结果** 标签页
   - 输入活动 ID 并点击 **查询**
   - 查看详细的执行结果

## 常用操作速查

### 创建活动
```
活动管理 → 填写表单 → 创建活动
```

### 启动活动
```
活动管理 → 选择活动 → 启动
```

### 监控进度
```
实时监控 → 开始监控 → 查看进度条和日志
```

### 查看结果
```
执行结果 → 输入活动ID → 查询 → 选择记录查看详情
```

### 检查系统
```
系统状态 → 健康检查 → 查看各组件状态
```

### 修改配置
```
配置 → 修改服务器地址 → 保存连接
```

## 协议快速参考

| 协议 | 默认端口 | 目标地址示例 |
|------|---------|-------------|
| CoAP | 5683 | `localhost:5683` |
| Modbus | 502 | `localhost:502` |
| MQTT | 1883 | `localhost:1883` |
| HTTP | 80/443 | `localhost:8000` |
| gRPC | 50051 | `localhost:50051` |
| JSON-RPC | 8545 | `localhost:8545` |

## 常见问题快速解决

### ❌ GUI 无法启动

**Ubuntu**: 安装 tkinter
```bash
sudo apt-get install python3-tk
```

**Windows**: 重新安装 Python（确保勾选 tkinter）

### ❌ 无法连接到服务器

1. 检查服务器是否运行：
```bash
curl http://localhost:8080/health
```

2. 检查防火墙设置

3. 在 GUI 中修改服务器地址（配置标签页）

### ❌ 活动创建失败

1. 确保所有字段都已填写
2. 检查目标地址格式
3. 确保 LLM 服务（Ollama）正在运行

### ❌ 监控数据不更新

1. 点击 "开始监控"
2. 确保活动已启动
3. 刷新活动列表

## 键盘快捷键

| 操作 | Windows | Linux/Mac |
|-----|---------|-----------|
| 刷新 | F5 | F5 |
| 帮助 | F1 | F1 |
| 退出 | Alt+F4 | Ctrl+Q |

## 下一步

- 📖 阅读完整 [README.md](README.md)
- 🔧 查看 [API.md](../API.md) 了解 API 详情
- 🏗️ 查看 [ARCHITECTURE.md](../ARCHITECTURE.md) 了解架构
- 🚀 查看 [DEPLOYMENT.md](../DEPLOYMENT.md) 了解部署

## 获取帮助

- 查看 GUI 内置帮助：菜单 → 帮助 → 关于
- 查看系统日志：系统状态标签页
- 报告问题：https://github.com/LuckyFu1111/HyFuzz/issues

---

**祝你使用愉快！Happy Fuzzing! 🚀**
