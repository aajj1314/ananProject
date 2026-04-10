#!/usr/bin/env python3
"""Simple verification script to check all modules import correctly."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("老人防丢鞋垫系统 - 简单验证")
print("=" * 60)

all_good = True

def check_import(name, module_path):
    global all_good
    try:
        __import__(module_path)
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        all_good = False
        return False

print("\n[1] 检查核心模块...")
check_import("Config", "app.config")
check_import("Database", "app.utils.database")
check_import("Security", "app.utils.security")
check_import("Errors", "app.utils.errors")
check_import("Response", "app.utils.response")

print("\n[2] 检查模型模块...")
check_import("User Model", "app.models.user")
check_import("Device Model", "app.models.device")
check_import("Location Model", "app.models.location")
check_import("Fence Model", "app.models.fence")
check_import("Alarm Model", "app.models.alarm")

print("\n[3] 检查 API 模块...")
check_import("Auth API", "app.api.v1.auth")
check_import("Device API", "app.api.v1.device")
check_import("Location API", "app.api.v1.location")
check_import("Fence API", "app.api.v1.fence")
check_import("Alarm API", "app.api.v1.alarm")
check_import("Health API", "app.api.v1.health")
check_import("Admin API", "app.api.v1.admin")

print("\n[4] 检查服务模块...")
check_import("User Service", "app.services.user_service")
check_import("Device Service", "app.services.device_service")
check_import("Location Service", "app.services.location_service")
check_import("Fence Service", "app.services.fence_service")
check_import("Alarm Service", "app.services.alarm_service")
check_import("Notification Service", "app.services.notification_service")

print("\n[5] 检查工具模块...")
check_import("Metrics", "app.utils.metrics")
check_import("Cache", "app.utils.cache")
check_import("Rate Limit", "app.utils.rate_limit")
check_import("Notifications Base", "app.utils.notifications.base")
check_import("In-App Notifications", "app.utils.notifications.in_app")
check_import("SMS Notifications", "app.utils.notifications.sms")
check_import("WeChat Notifications", "app.utils.notifications.wechat")

print("\n[6] 检查主应用...")
try:
    from app.main import app
    print(f"✅ FastAPI app created, title={app.title}")
except Exception as e:
    print(f"❌ Main app: {e}")
    all_good = False

print("\n" + "=" * 60)
if all_good:
    print("✅ 所有模块验证通过！")
else:
    print("❌ 部分模块验证失败")
print("=" * 60)

sys.exit(0 if all_good else 1)
