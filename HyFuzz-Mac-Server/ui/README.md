# HyFuzz 跨平台 GUI 界面

HyFuzz 的图形用户界面，支持 Windows 和 Ubuntu 系统，提供直观的操作界面来管理模糊测试活动、监控执行进度和查看结果。

## 🌟 功能特性

### 1. 活动管理
- ✅ 创建新的模糊测试活动
- ✅ 配置协议（CoAP, Modbus, MQTT, HTTP, gRPC, JSON-RPC）
- ✅ 设置目标地址和参数
- ✅ 启动、暂停、停止活动
- ✅ 查看活动列表和状态

### 2. 实时监控
- 📊 进度条显示执行进度
- 📈 统计信息实时更新
- 📝 实时日志查看
- 🎯 活动详细信息展示

### 3. 结果查看
- 🔍 执行结果查询和筛选
- 📋 详细信息查看
- 💾 结果导出功能
- 🏷️ 风险等级和判决展示

### 4. 系统状态
- 🏥 服务健康检查
- 🖥️ 系统资源监控
- 📊 组件状态展示
- 📜 系统日志查看

### 5. 配置管理
- ⚙️ 连接配置
- 🎨 界面主题切换
- 💾 默认参数设置
- 📄 配置导入导出

## 📋 系统要求

### 通用要求
- **Python**: 3.10 或更高版本
- **内存**: 至少 2GB RAM
- **网络**: 需要连接到 HyFuzz 服务器

### Windows 系统
- Windows 10 或更高版本
- Python 3.10+ (tkinter 已包含)

### Ubuntu 系统
- Ubuntu 20.04 LTS 或更高版本
- Python 3.10+
- tkinter (需要单独安装)

## 🚀 快速开始

### 1. 安装依赖

#### Ubuntu 系统
```bash
# 安装 tkinter
sudo apt-get update
sudo apt-get install python3-tk

# 安装 Python 依赖
cd /path/to/HyFuzz/ui
pip install -r requirements.txt
```

#### Windows 系统
```powershell
# tkinter 随 Python 一起安装，无需额外操作

# 安装 Python 依赖
cd C:\path\to\HyFuzz\ui
pip install -r requirements.txt
```

### 2. 启动 HyFuzz 服务器

在启动 GUI 之前，确保 HyFuzz 服务器正在运行：

#### Windows 控制平面
```bash
cd HyFuzz-Windows-Server
python scripts/start_server.py
```

#### Ubuntu 执行客户端
```bash
cd HyFuzz-Ubuntu-Client
python scripts/start_client.py
```

### 3. 启动 GUI

```bash
# 从 HyFuzz 根目录运行
python ui/launch_gui.py

# 或者直接运行
python ui/hyfuzz_gui.py
```

### 4. 检查依赖和服务器状态

```bash
python ui/launch_gui.py --check
```

## 📖 使用指南

### 创建模糊测试活动

1. 打开 **活动管理** 标签页
2. 在左侧表单中填写：
   - 活动名称
   - 协议类型（CoAP, Modbus, MQTT 等）
   - 目标地址（例如：localhost:5683）
   - Payload 数量
   - 超时时间
   - LLM 模型
3. 选择是否启用防御分析和判决反馈
4. 点击 **创建活动** 按钮

### 监控活动执行

1. 在 **活动管理** 中选择一个活动
2. 点击 **启动** 按钮开始执行
3. 切换到 **实时监控** 标签页
4. 点击 **开始监控** 按钮
5. 查看：
   - 进度条显示完成百分比
   - 统计信息（成功、失败、崩溃等）
   - 实时日志输出

### 查看执行结果

1. 打开 **执行结果** 标签页
2. 输入活动 ID
3. 选择筛选条件（可选）
4. 点击 **查询** 按钮
5. 在列表中选择一条记录查看详细信息

### 检查系统状态

1. 打开 **系统状态** 标签页
2. 点击 **健康检查** 按钮
3. 查看各个组件的状态：
   - MCP 服务器
   - Web 控制台
   - 任务队列
   - 数据库
   - 缓存
   - LLM 服务

### 配置服务器连接

1. 打开 **配置** 标签页
2. 修改服务器地址（默认：http://localhost:8080）
3. 修改控制台地址（默认：http://localhost:8888）
4. 点击 **保存连接** 按钮

## 🎨 界面预览

### 主界面布局

```
┌──────────────────────────────────────────────────────────────┐
│  文件  操作  帮助                                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  活动管理 │ 实时监控 │ 执行结果 │ 系统状态 │ 配置  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │                  标签页内容区域                      │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  状态: 就绪                              ● 已连接           │
└──────────────────────────────────────────────────────────────┘
```

### 活动管理标签

- **左侧**: 创建新活动表单
- **右侧**: 活动列表和控制按钮

### 实时监控标签

- **顶部**: 当前活动信息
- **中部**: 进度条和统计信息
- **底部**: 实时日志输出

## 🔧 高级功能

### 导入配置文件

1. 点击菜单 **文件 > 导入配置**
2. 选择 YAML 或 JSON 配置文件
3. 配置将自动加载到表单中

### 导出执行结果

1. 在 **执行结果** 标签页查询结果
2. 点击菜单 **文件 > 导出结果**
3. 选择导出格式（JSON 或 CSV）
4. 保存文件

### 切换界面主题

1. 打开 **配置** 标签页
2. 在 **界面主题** 部分选择主题
3. 点击 **应用主题** 按钮

可用主题：
- `clam` (默认)
- `alt`
- `default`
- `classic`

## 🐛 故障排除

### GUI 无法启动

**问题**: 提示 tkinter 未安装

**解决方案**:
```bash
# Ubuntu
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

**问题**: 提示 requests 未安装

**解决方案**:
```bash
pip install requests
```

### 无法连接到服务器

**问题**: 状态栏显示 "● 未连接"

**解决方案**:
1. 检查 HyFuzz 服务器是否正在运行
2. 检查服务器地址配置是否正确
3. 检查防火墙设置
4. 检查端口 8080 是否被占用

```bash
# 检查端口
netstat -ano | grep 8080  # Linux
netstat -ano | findstr 8080  # Windows
```

### 活动创建失败

**问题**: 点击创建活动后没有响应或报错

**解决方案**:
1. 检查表单是否填写完整
2. 检查目标地址格式是否正确
3. 查看系统日志了解详细错误信息
4. 确保 LLM 服务（Ollama）正在运行

### 监控数据不更新

**问题**: 进度条和统计信息不变化

**解决方案**:
1. 确保已点击 "开始监控"
2. 检查活动是否真的在执行
3. 尝试刷新活动列表
4. 重新启动 GUI

## 📚 API 集成

GUI 通过 REST API 与 HyFuzz 服务器通信。主要端点：

```python
# 健康检查
GET /health

# 活动管理
POST   /api/v1/campaigns          # 创建活动
GET    /api/v1/campaigns          # 列表活动
GET    /api/v1/campaigns/{id}     # 获取详情
POST   /api/v1/campaigns/{id}/start   # 启动
POST   /api/v1/campaigns/{id}/pause   # 暂停
POST   /api/v1/campaigns/{id}/stop    # 停止
DELETE /api/v1/campaigns/{id}     # 删除

# 统计和结果
GET /api/v1/campaigns/{id}/statistics  # 统计信息
GET /api/v1/campaigns/{id}/executions  # 执行结果
```

## 🔒 安全注意事项

1. **不要在公网暴露**: GUI 和服务器仅供本地或受信任网络使用
2. **API 密钥**: 生产环境应配置 API 密钥认证
3. **HTTPS**: 建议在生产环境使用 HTTPS
4. **输入验证**: GUI 会进行基本输入验证，但服务器端也应有验证

## 🤝 贡献

欢迎提交问题和改进建议：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License - 查看 [LICENSE](../LICENSE) 文件了解详情

## 📞 支持

- **问题报告**: [GitHub Issues](https://github.com/LuckyFu1111/HyFuzz/issues)
- **文档**: [HyFuzz Documentation](../docs/)
- **邮件**: support@hyfuzz.example.com

## 🎯 路线图

### 即将推出的功能

- [ ] 图表和可视化（使用 matplotlib）
- [ ] 暗色主题支持
- [ ] 多语言支持（i18n）
- [ ] 活动模板管理
- [ ] 批量操作支持
- [ ] 高级筛选和搜索
- [ ] 导出 HTML 报告
- [ ] 实时通知和警报
- [ ] 集成终端控制台
- [ ] 配置文件编辑器

### 已知限制

- 不支持实时 WebSocket 流（计划中）
- 图表功能需要额外依赖（可选）
- 大数据集可能导致性能下降（待优化）

## 🙏 致谢

- [Python Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI 框架
- [Requests](https://requests.readthedocs.io/) - HTTP 库
- HyFuzz 开发团队和贡献者

---

**Happy Fuzzing! 🐛🔍**
