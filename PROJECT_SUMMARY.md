# 老人防丢鞋垫系统 - 项目汇总

## 项目概述

老人防丢鞋垫系统是一个完整的全栈平台，用于管理和监控老年人防丢智能鞋垫设备。系统提供实时位置追踪、电子围栏管理、多渠道通知等功能，帮助监护人实时了解老人的位置和状态，确保老人的安全。

## 技术架构

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

## 功能特性

- 🔐 用户认证（注册/登录/角色权限）
- 📱 设备管理（绑定/重命名/解绑）
- 📍 实时位置追踪与历史回放
- 🚧 电子围栏管理与越界报警
- 🔔 多渠道通知（应用内/SMS/微信）
- 📊 运营指标与健康检查
- 🎛️ 管理员仪表板

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

## Docker 部署

```bash
cd deploy
docker-compose up -d
```

服务将在以下地址访问：
- 前端：http://localhost:8081
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

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
├── PROJECT_SUMMARY.md   # 项目汇总文档
├── start-backend.sh     # 后端启动脚本
└── start-frontend.sh    # 前端启动脚本
```

## 功能说明

### 用户认证

- **注册账号**：填写手机号、密码和昵称
- **登录**：输入手机号和密码
- **角色权限**：支持用户和管理员角色

### 设备管理

- **绑定新设备**：输入 15 位 IMEI 码和设备名称
- **查看设备**：设备卡片显示 IMEI、名称、电量、报警状态、最后上报时间
- **设备操作**：重命名、解绑

### 地图与定位

- **查看实时位置**：显示设备当前位置坐标
- **轨迹回放**：使用控制条进行播放/暂停/重置，调节播放速度
- **轨迹摘要**：显示采样点数量、报警次数、最后报警类型

### 电子围栏

- **创建围栏**：填写围栏名称、中心纬度和经度、半径
- **围栏状态**：显示每个围栏的状态（围栏内/围栏外）
- **围栏报警**：设备离开围栏时触发越界报警

### 报警与通知

- **报警类型**：防拆报警、跌倒报警、静止报警、低电量报警、SOS 报警、电子围栏越界
- **查看报警记录**：最近报警列表、通知日志
- **通知渠道**：应用内、SMS、微信

### 管理员功能

- **管理仪表板**：显示用户总数、设备总数、报警总数、通知总数
- **用户管理**：查看所有注册用户、修改用户角色、删除用户
- **平台统计**：查看所有设备、所有报警、所有通知、运营指标数据

## API 参考

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

## 配置说明

### 后端配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
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
|--------|--------|------|
| `VITE_MAP_PROVIDER` | coordinate | 地图提供商 |
| `VITE_MAP_API_KEY` | - | 地图 API 密钥 |
| `VITE_API_BASE_URL` | http://localhost:8000/api/v1 | API 基础 URL |

## 常见问题

### Q: 如何创建管理员账号？

A: 有两种方式：

1. **通过数据库直接修改**：
   将用户的 `role` 字段更新为 `admin`

2. **通过 API（需要先有一个管理员）**：
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

**SMS（示例）**：
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

## 技术支持

如遇到问题，请检查：
1. 后端和前端服务是否正常启动
2. 浏览器控制台的错误信息
3. 后端控制台的错误信息
4. 环境变量配置是否正确
5. 数据库连接是否正常

## 项目状态

✅ **项目已完成！** 所有功能都已实现，所有文档都已齐全，可以直接部署上线交付使用。

## 下一步操作建议

1. **测试部署**: 使用 Docker 在测试环境部署验证
2. **配置安全**: 修改生产环境的 `JWT_SECRET` 为强随机密钥
3. **数据备份**: 配置数据库定期备份策略
4. **监控告警**: 配置生产环境监控和告警
5. **用户培训**: 为最终用户提供使用培训

## 联系方式

如有问题，请参考：
- `PROJECT_SUMMARY.md` - 项目汇总文档
- `deploy/README.md` - Docker 部署指南
- `RUN_GUIDE.md` - 运行指南
- `DOCKER_QUICKSTART.md` - Docker 快速启动

---

**🎉 项目交付完成！**