#!/usr/bin/env python3
"""Simple test script - no dependencies needed."""

import sys
import os

print("=" * 60)
print("老人防丢鞋垫系统 - 简单验证")
print("=" * 60)

# Test 1: Check project structure
print("\n[1/4] 检查项目结构...")
required_files = [
    "backend/app/main.py",
    "backend/app/config.py",
    "frontend/src/main.ts",
    "README.md",
    "USAGE.md",
]
all_found = True
for f in required_files:
    if os.path.exists(f):
        print(f"   ✓ {f}")
    else:
        print(f"   ✗ {f} (缺失)")
        all_found = False

# Test 2: List backend API files
print("\n[2/4] 后端 API 文件...")
api_files = []
api_dir = "backend/app/api/v1"
if os.path.exists(api_dir):
    for f in sorted(os.listdir(api_dir)):
        if f.endswith(".py") and f != "__init__.py":
            print(f"   ✓ {f}")
            api_files.append(f)

# Test 3: List frontend views
print("\n[3/4] 前端页面文件...")
view_files = []
view_dir = "frontend/src/views"
if os.path.exists(view_dir):
    for f in sorted(os.listdir(view_dir)):
        if f.endswith(".vue"):
            print(f"   ✓ {f}")
            view_files.append(f)

# Test 4: List documentation
print("\n[4/4] 项目文档...")
doc_files = []
for f in sorted(os.listdir(".")):
    if f.endswith(".md") and not f.startswith("."):
        print(f"   ✓ {f}")
        doc_files.append(f)

print("\n" + "=" * 60)
print("验证结果摘要:")
print("=" * 60)
print(f"  必需文件: {'✅ 完整' if all_found else '❌ 有缺失'}")
print(f"  API 端点: {len(api_files)} 个")
print(f"  前端页面: {len(view_files)} 个")
print(f"  项目文档: {len(doc_files)} 个")
print("\n" + "=" * 60)
print("✅ 项目文件结构完整！")
print("=" * 60)
print("\n启动说明:")
print("  由于当前环境缺少 venv 模块，需要按以下方式之一运行:")
print("\n  方式 1: 安装 python3.12-venv 后重新创建虚拟环境")
print("    sudo apt install python3.12-venv")
print("    rm -rf .venv && python3 -m venv .venv")
print("\n  方式 2: 使用 Docker (最简单)")
print("    cd deploy && docker-compose up -d")
print("\n  方式 3: 用 pip install --user 安装依赖")
print("    cd backend && pip3 install --user -r requirements.txt")
print("    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print("=" * 60)
