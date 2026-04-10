#!/usr/bin/env python3
"""Quick verification script to test backend imports."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("老人防丢鞋垫系统 - 后端验证")
print("=" * 60)

try:
    print("\n[1/5] 测试 FastAPI 导入...")
    import fastapi
    print(f"   ✓ FastAPI {fastapi.__version__}")

    print("\n[2/5] 测试 SQLAlchemy 导入...")
    import sqlalchemy
    print(f"   ✓ SQLAlchemy {sqlalchemy.__version__}")

    print("\n[3/5] 测试 Pydantic 导入...")
    import pydantic
    print(f"   ✓ Pydantic {pydantic.__version__}")

    print("\n[4/5] 测试后端主模块导入...")
    import app.main
    print("   ✓ app.main 导入成功")

    print("\n[5/5] 测试 API 路由导入...")
    from app.api.v1 import auth, device, location, fence, alarm, health, admin
    print("   ✓ 所有 API 路由导入成功")

    print("\n" + "=" * 60)
    print("✅ 后端验证通过！所有模块导入成功！")
    print("=" * 60)
    print("\n可以使用以下命令启动后端:")
    print("  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI 文档将在: http://localhost:8000/docs")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ 错误: {type(e).__name__}: {e}")
    import traceback
    print("\n详细错误信息:")
    print(traceback.format_exc())
    sys.exit(1)
