# 老人防丢鞋垫系统 使用说明书

## 目录

- [系统概述](#系统概述)
- [快速开始](#快速开始)
- [功能说明](#功能说明)
- [API 参考](#api-参考)
- [部署指南](#部署指南)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 系统概述

### 什么是老人防丢鞋垫系统？

这是一个完整的全栈平台，用于管理和监控老年人防丢智能鞋垫设备。系统提供：

- 用户注册与登录
- 设备绑定与管理
- 实时位置追踪
- 位置历史回放
- 电子围栏设置
- 报警与通知
- 管理员仪表板

### 技术架构

**后端**
- FastAPI (Python 3.12+)
- SQLAlchemy 2.0 (异步 ORM)
- SQLite/MySQL 数据库
- Redis 缓存（可选）
- JWT 认证

**前端**
- Vue 3 + TypeScript
- Vite 构建工具
- Pinia 状态管理
- Vue Router 路由

---

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- npm 或 yarn

### 后端启动

#### 1. 克隆项目

```bash
cd ananProject
```

#### 2. 设置虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
# 复制开发环境配置
cp ../.env.development.example .env
```

根据需要编辑 `.env` 文件中的配置项。

#### 5. 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动。

访问 API 文档：http://localhost:8000/docs

### 前端启动

#### 1. 安装前端依赖

```bash
cd frontend
npm install
```

#### 2. 配置环境变量（可选）

```bash
cp .env.example .env
```

#### 3. 启动前端开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 启动。

### 使用启动脚本（推荐）

项目提供了便捷的启动脚本：

```bash
# 启动后端
./start-backend.sh

# 在另一个终端启动前端
./start-frontend.sh
```

---

## 功能说明

### 用户认证

#### 注册账号

1. 访问登录页面
2. 点击"注册账号"
3. 填写手机号、密码和昵称
4. 点击"注册"

#### 登录

1. 输入手机号和密码
2. 点击"进入平台"

### 设备管理

#### 绑定新设备

1. 登录后进入设备列表页
2. 在"绑定新设备"区域
3. 输入 15 位 IMEI 码
4. 输入设备名称（如"爸爸的鞋垫"）
5. 点击"绑定设备"

#### 查看设备

- 设备卡片显示：IMEI、名称、电量、报警状态、最后上报时间
- 点击"查看地图"进入设备详情页

#### 设备操作

- **重命名**：修改设备名称
- **解绑**：移除设备绑定

### 地图与定位

#### 查看实时位置

1. 在设备列表点击"查看地图"
2. 顶部显示设备当前位置坐标
- 纬度、经度、电量、报警类型、上报时间

#### 轨迹回放

1. 在地图页点击"回放轨迹"
2. 使用控制条进行播放/暂停/重置
3. 调节播放速度（0.5x - 5x）
4. 拖动进度条跳转到指定位置

#### 轨迹摘要

- 采样点数量
- 报警次数
- 最后报警类型

### 电子围栏

#### 创建围栏

1. 在地图页的"围栏配置"区域
2. 填写围栏名称
3. 输入中心纬度和经度
4. 设置半径（单位：米）
5. 勾选"启用"
6. 点击"创建围栏"

#### 围栏状态

- 显示每个围栏的状态（围栏内/围栏外）
- 显示距离中心点的距离
- 状态切换时会显示提示

#### 围栏报警

当设备离开启用的围栏时：
- 系统自动记录围栏越界报警
- 生成通知记录
- 避免重复报警（同一状态持续时）

### 报警与通知

#### 报警类型

| 报警类型 | 说明
|---------|------
| 1 | 防拆报警
| 2 | 跌倒报警
| 3 | 静止报警
| 4 | 低电量报警（< 20%）
| 5 | SOS 报警
| 6 | 电子围栏越界

#### 查看报警记录

在地图页可以查看：
- 最近报警列表
- 通知日志

#### 通知渠道

系统支持多渠道通知：
- **应用内**：默认启用
- **SMS**：需配置 SMS 提供商
- **微信**：需配置微信公众号

### 管理员功能

#### 进入管理后台

管理员账号登录后，在设备列表页点击"管理后台"。

#### 管理仪表板显示

- 用户总数
- 设备总数
- 报警总数
- 通知总数

#### 用户管理

- 查看所有注册用户
- 修改用户角色（设为管理员/取消管理员）
- 删除用户（不能删除自己）

#### 平台统计

- 查看所有设备
- 查看所有报警
- 查看所有通知
- 运营指标数据

---

## API 参考

### 认证接口

#### 注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "passw0rd",
  "nickname": "监护人"
}
```

#### 登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "passw0rd"
}
```

#### 获取当前用户资料
```http
GET /api/v1/auth/profile
Authorization: Bearer <token>
```

### 设备接口

#### 获取设备列表
```http
GET /api/v1/device
Authorization: Bearer <token>
```

#### 绑定设备
```http
POST /api/v1/device
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_id": "123456789012345",
  "device_name": "爸爸的鞋垫"
}
```

#### 更新设备
```http
PUT /api/v1/device/{device_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_name": "新名称"
}
```

#### 解绑设备
```http
DELETE /api/v1/device/{device_id}
Authorization: Bearer <token>
```

### 位置接口

#### 上传定位数据
```http
POST /api/v1/location/ingest
Content-Type: application/json

{
  "device_id": "123456789012345",
  "timestamp": "2026-04-10T10:00:00Z",
  "latitude": 39.1028,
  "longitude": 117.3475,
  "altitude": 50.5,
  "alarm_type": 0,
  "battery": 85,
  "speed": 1.2,
  "direction": 90
}
```

#### 获取最新位置
```http
GET /api/v1/location/{device_id}
Authorization: Bearer <token>
```

#### 获取位置历史
```http
GET /api/v1/location/history/{device_id}?start_time=<iso>&end_time=<iso>
Authorization: Bearer <token>
```

#### 获取位置摘要
```http
GET /api/v1/location/summary/{device_id}?start_time=<iso>&end_time=<iso>
Authorization: Bearer <token>
```

### 电子围栏接口

#### 获取围栏列表
```http
GET /api/v1/fence/{device_id}
Authorization: Bearer <token>
```

#### 创建围栏
```http
POST /api/v1/fence/{device_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "家",
  "center_latitude": 39.1028,
  "center_longitude": 117.3475,
  "radius_meters": 300,
  "is_active": true
}
```

#### 更新围栏
```http
PUT /api/v1/fence/{device_id}/{fence_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "家",
  "center_latitude": 39.1028,
  "center_longitude": 117.3475,
  "radius_meters": 500,
  "is_active": true
}
```

#### 删除围栏
```http
DELETE /api/v1/fence/{device_id}/{fence_id}
Authorization: Bearer <token>
```

### 报警接口

#### 获取设备最新报警
```http
GET /api/v1/alarm/{device_id}
Authorization: Bearer <token>
```

#### 获取报警历史
```http
GET /api/v1/alarm/history/{device_id}
Authorization: Bearer <token>
```

#### 获取通知历史
```http
GET /api/v1/alarm/notifications/{device_id}
Authorization: Bearer <token>
```

### 健康检查接口

#### 基础健康检查
```http
GET /health
GET /api/v1/health
```

#### 详细健康检查
```http
GET /api/v1/health/detailed
```

#### 获取运营指标
```http
GET /api/v1/health/metrics?window_seconds=60
```

### 管理员接口（仅管理员）

#### 获取用户列表
```http
GET /api/v1/admin/users?offset=0&limit=50
Authorization: Bearer <admin-token>
```

#### 修改用户角色
```http
PUT /api/v1/admin/users/{user_id}/role?role=admin
Authorization: Bearer <admin-token>
```

#### 获取平台统计
```http
GET /api/v1/admin/stats
Authorization: Bearer <admin-token>
```

---

## 部署指南

### Docker 部署

使用 docker-compose 一键部署：

```bash
cd deploy
docker-compose up -d
```

服务将启动后访问：
- 前端：http://localhost:8080
- 后端：http://localhost:8000

### 生产环境配置

生产环境建议：

1. **复制生产环境配置：
```bash
cp .env.production.example .env
```

2. **修改关键配置：
```env
DEBUG=false
JWT_SECRET=your-secure-random-secret-key
DATABASE_URL=mysql+aiomysql://user:password@db:3306/elderly_care
REDIS_URL=redis://redis:6379/0
```

3. **配置通知渠道（可选）：
```env
NOTIFICATION_CHANNELS=in_app,sms,wechat
SMS_PROVIDER=aliyun
SMS_API_KEY=your-api-key
SMS_FROM_NUMBER=your-sender
```

### 数据库选择

#### 开发环境
- 默认使用 SQLite，无需额外配置

#### 生产环境
- 推荐使用 MySQL 8.0+
- 配置 `DATABASE_URL` 环境变量

### Redis 配置（可选）

Redis 用于：
- 请求速率限制
- 缓存
- 如果不可用时自动降级到内存实现

---

## 配置说明

### 后端配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------
| `APP_NAME` | elderly-insole-platform | 应用名称 |
| `APP_ENV` | development | 运行环境 |
| `DEBUG` | true | 调试模式 |
| `DATABASE_URL` | sqlite+aiosqlite:///./elderly_insole_dev.db | 数据库连接 |
| `REDIS_URL` | redis://localhost:6379/1 | Redis 连接 |
| `JWT_SECRET` | dev-secret-key | JWT 密钥（生产环境必须修改） |
| `JWT_ALGORITHM` | HS256 | JWT 算法 |
| `JWT_EXPIRE_MINUTES` | 1440 | Token 有效期（分钟） |
| `NOTIFICATION_CHANNELS` | ["in_app"] | 启用的通知渠道 |
| `SMS_PROVIDER` | - | SMS 提供商 |
| `SMS_API_KEY` | - | SMS API 密钥 |
| `SMS_FROM_NUMBER` | - | SMS 发送号码 |
| `WECHAT_APP_ID` | - | 微信公众号 AppID |
| `WECHAT_APP_SECRET` | - | 微信公众号密钥 |
| `WECHAT_TEMPLATE_ID` | - | 微信消息模板 ID |
| `RATE_LIMIT_REQUESTS` | 60 | 速率限制请求数 |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 | 速率限制窗口（秒） |
| `CACHE_TTL_SECONDS` | 120 | 缓存 TTL（秒） |

### 前端配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------
| `VITE_MAP_PROVIDER` | coordinate | 地图提供商 |
| `VITE_MAP_API_KEY` | - | 地图 API 密钥 |
| `VITE_API_BASE_URL` | http://localhost:8000/api/v1 | API 基础 URL |

---

## 常见问题

### Q: 如何创建管理员账号？

A: 有两种方式：

1. **通过数据库直接修改**：
   将用户的 `role` 字段更新为 `admin`

2. **通过 API（需要先有一个管理员）：
   使用管理员账号调用 `PUT /api/v1/admin/users/{user_id}/role?role=admin`

### Q: 电子围栏是如何工作的？

A: 系统使用圆形围栏：
- 中心点经纬度 + 半径（米）定义围栏范围
- 使用 Haversine 公式计算两点间距离
- 设备离开围栏时触发越界报警
- 同一状态持续时不会重复报警

### Q: 如何集成真实地图 SDK？

A: 1. 在 `frontend/.env` 设置：
```env
VITE_MAP_PROVIDER=amap  # 或 baidu
VITE_MAP_API_KEY=your-api-key
```

2. 在 `MapView.vue` 中实现对应地图组件

### Q: 通知如何配置 SMS/微信通知？

A: 在 `.env` 中配置：

**SMS（示例）：
```env
NOTIFICATION_CHANNELS=in_app,sms
SMS_PROVIDER=aliyun
SMS_API_KEY=your-key
SMS_FROM_NUMBER=your-number
```

**微信**：
```env
NOTIFICATION_CHANNELS=in_app,wechat
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-secret
WECHAT_TEMPLATE_ID=your-template-id
```

### Q: 数据存储在哪里？

A: 默认使用 SQLite 数据库文件：`backend/elderly_insole_dev.db`

生产环境建议使用 MySQL。

### Q: 如何备份数据？

A: 1. **SQLite**：直接复制 `.db` 文件

2. **MySQL**：使用 `mysqldump`

### Q: 忘记密码怎么办？

A: 目前需要通过数据库重置：
- 更新用户的 `password` 字段（使用 `hash_password()` 生成新哈希）

### Q: 如何查看日志？

A: 后端日志输出到控制台。生产环境建议配置日志收集。

### Q: 支持哪些浏览器？

A: 推荐使用：
- Chrome/Edge (最新版)
- Firefox (最新版)
- Safari (最新版)

---

## 技术支持

如遇到问题，请检查：
1. 后端和前端服务是否正常启动
2. 浏览器控制台的错误信息
3. 后端控制台的错误信息
4. 环境变量配置是否正确
5. 数据库连接是否正常

---

*文档版本: 1.0 | 更新日期: 2026-04-10
