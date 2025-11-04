#!/usr/bin/env python3
"""
HyFuzz GUI 启动脚本
跨平台支持 Windows 和 Ubuntu
"""

import sys
import os
import platform
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖项"""
    print("检查系统依赖...")

    # 检查 Python 版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"错误: 需要 Python 3.10 或更高版本，当前版本: {version.major}.{version.minor}")
        return False

    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")

    # 检查 tkinter
    try:
        import tkinter as tk
        print("✓ tkinter 已安装")
    except ImportError:
        print("错误: tkinter 未安装")
        system = platform.system()
        if system == "Linux":
            print("请运行: sudo apt-get install python3-tk")
        elif system == "Windows":
            print("tkinter 应该随 Python 一起安装。请重新安装 Python。")
        return False

    # 检查 requests
    try:
        import requests
        print("✓ requests 已安装")
    except ImportError:
        print("错误: requests 未安装")
        print("请运行: pip install requests")
        return False

    return True


def setup_environment():
    """设置环境"""
    # 添加项目根目录到 Python 路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # 设置工作目录
    os.chdir(project_root)

    print(f"工作目录: {project_root}")
    print(f"系统平台: {platform.system()} {platform.release()}")


def check_server_status():
    """检查服务器状态"""
    try:
        import requests
        response = requests.get("http://localhost:8080/health", timeout=3)
        if response.status_code == 200:
            print("✓ HyFuzz 服务器正在运行")
            return True
        else:
            print("⚠ HyFuzz 服务器响应异常")
            return False
    except:
        print("⚠ HyFuzz 服务器未运行")
        print("\n提示: 请先启动 HyFuzz 服务器")
        print("  - Windows: cd HyFuzz-Windows-Server && python scripts/start_server.py")
        print("  - Ubuntu: cd HyFuzz-Ubuntu-Client && python scripts/start_client.py")
        return False


def launch_gui():
    """启动 GUI"""
    print("\n" + "=" * 60)
    print("启动 HyFuzz GUI...")
    print("=" * 60 + "\n")

    try:
        # 导入并运行 GUI
        from ui.hyfuzz_gui import main
        main()
    except KeyboardInterrupt:
        print("\n\nGUI 已关闭")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def show_help():
    """显示帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════════════════════╗
║                     HyFuzz GUI 启动器                                ║
╚══════════════════════════════════════════════════════════════════════╝

使用方法:
  python ui/launch_gui.py              启动 GUI
  python ui/launch_gui.py --help       显示此帮助信息
  python ui/launch_gui.py --check      仅检查依赖和服务器状态

系统要求:
  • Python 3.10 或更高版本
  • tkinter (Python GUI 库)
  • requests (HTTP 客户端)

支持的操作系统:
  • Windows 10/11
  • Ubuntu 20.04+
  • macOS 10.15+ (理论上支持)

启动前准备:
  1. 确保 HyFuzz 服务器正在运行
  2. 检查端口 8080 (MCP Server) 可用
  3. 检查端口 8888 (Dashboard) 可用

如果遇到问题:
  • 检查 Python 版本: python --version
  • 安装依赖: pip install -r requirements.txt
  • 查看日志: 日志显示在 GUI 的各个标签页中
  • 报告问题: https://github.com/LuckyFu1111/HyFuzz/issues

更多信息请参阅: README.md
    """
    print(help_text)


def main():
    """主函数"""
    # 解析命令行参数
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        return

    print("\n" + "=" * 60)
    print("HyFuzz - 智能分布式模糊测试平台")
    print("跨平台 GUI 界面")
    print("=" * 60 + "\n")

    # 设置环境
    setup_environment()

    # 检查依赖
    if not check_dependencies():
        print("\n依赖检查失败，请安装缺失的依赖项")
        sys.exit(1)

    # 检查服务器状态
    check_server_status()

    if "--check" in sys.argv:
        print("\n检查完成")
        return

    # 启动 GUI
    print("\n正在启动 GUI，请稍候...\n")
    success = launch_gui()

    if success:
        print("\n感谢使用 HyFuzz!")
    else:
        print("\nGUI 启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
