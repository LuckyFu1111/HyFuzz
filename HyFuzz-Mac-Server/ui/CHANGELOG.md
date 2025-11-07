# HyFuzz GUI 更新日志

本文档记录 HyFuzz 图形用户界面的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2025-11-04

### 新增
- ✨ 首次发布跨平台 GUI 界面
- 🎨 支持 Windows 和 Ubuntu 系统
- 📋 活动管理功能
  - 创建新活动
  - 配置协议（CoAP, Modbus, MQTT, HTTP, gRPC, JSON-RPC）
  - 启动、暂停、停止、删除活动
  - 活动列表查看
- 📊 实时监控功能
  - 进度条显示
  - 统计信息展示
  - 实时日志输出
  - 活动信息查看
- 🔍 结果查看功能
  - 执行结果查询
  - 结果筛选
  - 详细信息展示
  - 支持导出（规划中）
- 🏥 系统状态功能
  - 健康检查
  - 服务状态监控
  - 系统资源显示（规划中）
  - 系统日志查看
- ⚙️ 配置管理功能
  - 连接配置
  - 默认参数设置
  - 主题切换
  - 配置导入导出（规划中）
- 📖 完整的文档
  - README.md - 完整使用手册
  - QUICKSTART.md - 快速入门指南
  - CHANGELOG.md - 更新日志

### 技术特性
- 🐍 使用 Python 3.10+ 和 tkinter
- 🌐 通过 REST API 与服务器通信
- 🔄 自动连接状态检查
- 🎯 响应式界面设计
- 🔒 基本的输入验证

### 已知问题
- 大数据集可能导致性能下降
- 暂不支持 WebSocket 实时流
- 图表功能需要额外依赖

## [未发布]

### 计划新增
- [ ] 图表和可视化（matplotlib 集成）
- [ ] 暗色主题支持
- [ ] 多语言支持（i18n）
- [ ] 活动模板管理
- [ ] 批量操作支持
- [ ] 高级筛选和搜索
- [ ] 导出 HTML 报告
- [ ] 实时通知和警报
- [ ] 集成终端控制台
- [ ] 配置文件编辑器
- [ ] WebSocket 实时流支持
- [ ] 性能优化（虚拟化大数据集）

### 计划改进
- [ ] 更好的错误处理和用户反馈
- [ ] 更多的键盘快捷键
- [ ] 拖放文件支持
- [ ] 自动保存和恢复会话
- [ ] 更多的配置选项

---

## 版本说明

### 语义化版本格式：`主版本.次版本.修订号`

- **主版本号（Major）**: 不兼容的 API 修改
- **次版本号（Minor）**: 向下兼容的功能性新增
- **修订号（Patch）**: 向下兼容的问题修正

### 类型标识

- `新增` - 新功能
- `变更` - 现有功能的变化
- `弃用` - 即将移除的功能
- `移除` - 已移除的功能
- `修复` - 错误修复
- `安全` - 安全相关的修复

---

## 贡献

如果你想为 HyFuzz GUI 做贡献，请：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 反馈

如果你发现任何问题或有改进建议，请：

- 提交 Issue: https://github.com/LuckyFu1111/HyFuzz/issues
- 发送邮件: support@hyfuzz.example.com
- 加入讨论: https://github.com/LuckyFu1111/HyFuzz/discussions

---

**感谢使用 HyFuzz GUI！**
