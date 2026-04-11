# Elderly Insole Platform

老人防丢鞋垫系统 - 完整的全栈平台

## 项目状态

✅ **项目已完成！** 所有 Phase 1-5 的功能都已实现。

## 功能特性

- 🔐 用户认证（注册/登录/角色权限）
- 📱 设备管理（绑定/重命名/解绑）
- 📍 实时位置追踪与历史回放
- 🚧 电子围栏管理与越界报警
- 🔔 多渠道通知（应用内/SMS/微信）
- 📊 运营指标与健康检查
- 🎛️ 管理员仪表板

## 文档

- [快速启动指南](./QUICKSTART.md) - 快速上手
- [使用说明书](./USAGE.md) - 详细使用说明
- [项目路线图](./PROJECT_ROADMAP.md) - 开发计划
- [工作日志](./WORKLOG.md) - 开发记录
- [项目记忆](./PROJECT_MEMORY.md) - 项目状态记忆

## 快速开始

### 使用启动脚本（推荐，Linux 环境）

```bash
# 启动后端
./start-backend.sh

# 在另一个终端启动前端
./start-frontend.sh
```

### 手动启动

#### 后端（Linux/Windows 环境）

```bash
cd backend

# 1. 配置环境
# Linux
cp ../.env.development.example .env
# Windows
copy ..\.env.development.example .env

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 运行，API 文档在 http://localhost:8000/docs

#### 前端（Linux/Windows 环境）

```bash
cd frontend

# 1. 配置环境（可选）
# Linux
cp .env.example .env
# Windows
copy .env.example .env

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端将在 http://localhost:8081 运行

## 注意事项（Windows 环境）

1. **Python 3.13 兼容性**：项目在 Python 3.13 环境下需要使用较新版本的依赖包。
2. **环境变量配置**：在 Windows 环境下，`.env` 文件中的 `NOTIFICATION_CHANNELS` 字段需要使用 JSON 格式。
3. **依赖安装**：在 Windows 环境下安装依赖时，可能会遇到 pydantic-core 构建问题，建议使用预编译的二进制包。

详细说明请参考 [快速启动指南](./QUICKSTART.md)。

### Docker 部署

```bash
cd deploy
docker-compose up -d
```

## 项目结构

```
ananProject/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 端点
│   │   ├── models/      # ORM 模型
│   │   ├── schemas/     # Pydantic 模式
│   │   ├── services/    # 业务逻辑层
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面
│   │   ├── stores/      # 状态管理
│   │   ├── api/         # API 客户端
│   │   └── router/      # 路由
│   ├── Dockerfile
│   └── package.json
├── deploy/              # Docker 部署
│   └── docker-compose.yml
├── QUICKSTART.md        # 快速启动指南
├── USAGE.md            # 使用说明书
├── PROJECT_ROADMAP.md  # 项目路线图
├── WORKLOG.md          # 工作日志
├── PROJECT_MEMORY.md   # 项目记忆
├── start-backend.sh    # 后端启动脚本
└── start-frontend.sh   # 前端启动脚本
```

## 技术栈

### 后端
- FastAPI 0.110.0
- SQLAlchemy 2.0.49 (异步)
- Pydantic 2.12.5
- Pydantic Settings 2.13.1
- JWT 认证
- Redis 缓存（可选）

### 前端
- Vue 3.4 + TypeScript
- Vite 5.2
- Pinia 2.1
- Vue Router 4.3

### 容器化
- Docker
- Docker Compose

## 本地开发

后端默认使用本地 SQLite 异步数据库，无需额外配置。
生产环境的 MySQL、Redis 和 InfluxDB 配置可通过环境变量设置。

详细配置说明请参考 [使用说明书](./USAGE.md)。

## 许可证

本项目为老人防丢鞋垫系统的完整实现。

