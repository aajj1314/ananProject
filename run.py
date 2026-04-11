#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import time

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 后端目录
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
# 前端目录
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')

# 检测当前操作系统
def get_os():
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    else:
        return 'unknown'

# 启动后端服务
def start_backend():
    print("\n=== 启动后端服务 ===")
    os_type = get_os()
    
    if os_type == 'windows':
        # Windows 环境
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'start-backend.ps1']
        cwd = PROJECT_ROOT
    else:
        # Linux/macOS 环境
        cmd = ['bash', 'start-backend.sh']
        cwd = PROJECT_ROOT
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"工作目录: {cwd}")
    
    try:
        subprocess.Popen(cmd, cwd=cwd)
        print("后端服务已启动")
        return True
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return False

# 启动前端服务
def start_frontend():
    print("\n=== 启动前端服务 ===")
    os_type = get_os()
    
    if os_type == 'windows':
        # Windows 环境
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'start-frontend.ps1']
        cwd = PROJECT_ROOT
    else:
        # Linux/macOS 环境
        cmd = ['bash', 'start-frontend.sh']
        cwd = PROJECT_ROOT
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"工作目录: {cwd}")
    
    try:
        subprocess.Popen(cmd, cwd=cwd)
        print("前端服务已启动")
        return True
    except Exception as e:
        print(f"启动前端服务失败: {e}")
        return False

# 主函数
def main():
    print("=== 老人防丢鞋垫系统一键启动脚本 ===")
    print(f"当前操作系统: {get_os()}")
    print(f"项目根目录: {PROJECT_ROOT}")
    
    # 启动后端服务
    backend_success = start_backend()
    
    # 等待后端服务启动
    if backend_success:
        print("\n等待后端服务启动...")
        time.sleep(3)
    
    # 启动前端服务
    frontend_success = start_frontend()
    
    print("\n=== 启动完成 ===")
    print("服务访问地址:")
    print("- 后端服务: http://localhost:8000")
    print("- 前端服务: http://localhost:8080")
    print("- API 文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 退出脚本")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n退出脚本...")
        sys.exit(0)

if __name__ == "__main__":
    main()
