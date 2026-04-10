# 快速启动指南

## 项目状态

✅ **项目已完成！** 所有 Phase 1-5 的功能都已实现。

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
# 启动后端
./start-backend.sh

# 在另一个终端启动前端
./start-frontend.sh
```

### 方式二：手动启动

#### 后端启动

```bash
cd backend

# 1. 配置环境（复制示例配置）
cp ../.env.development.example .env

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 运行，API 文档在 http://localhost:8000/docs

#### 前端启动

```bash
cd frontend

# 1. 配置环境（可选）
cp .env.example .env

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 运行

## 功能清单

### 已实现功能

✅ 用户认证（注册/登录）
✅ 设备管理（绑定/重命名/解绑）
✅ 定位数据上传和查询
✅ 位置历史和摘要
✅ 电子围栏管理和越界报警
✅ 报警记录和通知日志
✅ 基于角色的访问控制（用户/管理员）
✅ 多渠道通知（应用内/SMS/微信）
✅ 运营指标和健康检查
✅ 轨迹回放模式
✅ 管理员仪表板

### 默认用户

注册任意用户即可使用。第一个注册的用户不会自动成为管理员，需要通过数据库或 API 手动设置。

## API 端点

### 公开端点
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /health` - 健康检查
- `POST /api/v1/location/ingest` - 定位数据上传

### 需要认证的端点
- `GET /api/v1/auth/profile` - 当前用户资料
- `GET/POST/PUT/DELETE /api/v1/device/*` - 设备管理
- `GET /api/v1/location/*` - 位置查询
- `GET /api/v1/alarm/*` - 报警查询
- `GET/POST/PUT/DELETE /api/v1/fence/*` - 电子围栏管理
- `GET /api/v1/health/*` - 健康检查和指标

### 仅管理员端点
- `GET /api/v1/admin/*` - 平台管理

## 环境变量配置

查看 `.env.development.example` 和 `.env.production.example` 了解所有可用配置项。

## Docker 部署

```bash
cd deploy
docker-compose up -d
```
