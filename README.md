# 老人防丢鞋垫系统

## 项目概述

老人防丢鞋垫系统是一个完整的全栈平台，用于管理和监控老年人防丢智能鞋垫设备。系统提供实时位置追踪、电子围栏管理、多渠道通知等功能，帮助监护人实时了解老人的位置和状态，确保老人的安全。

## 技术架构

### 后端
- FastAPI 0.110.0
- SQLAlchemy 2.0.49 (异步 ORM)
- Pydantic 2.12.5 + Pydantic Settings 2.13.1
- JWT 认证
- Redis 缓存（可选，自动降级）
- SQLite/MySQL 数据库

### 前端
- Vue 3.4 + TypeScript
- Vite 5.2
- Pinia 2.1 (状态管理)
- Vue Router 4.3
- Element Plus (UI 组件)
- Lucide Icons (图标库)

### 容器化
- Docker
- Docker Compose
- Nginx (前端代理)

## 功能特性

- 🔐 **用户认证**：注册、登录、角色权限管理
- 📱 **设备管理**：绑定、重命名、解绑设备
- 📍 **实时定位**：实时位置追踪、历史轨迹回放
- 🚧 **电子围栏**：自定义围栏、越界报警
- 🔔 **多渠道通知**：应用内、SMS、微信
- 📊 **运营指标**：健康检查、平台统计
- 🎛️ **管理员仪表板**：用户管理、设备管理、报警记录

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
cd deploy
chmod +x deploy.sh undeploy.sh
./deploy.sh start
```

### 方式二：本地运行

#### 后端启动

```bash
cd backend
cp ../.env.development.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## 访问地址

- **前端应用**：http://localhost:8081
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

## 默认登录信息

- **管理员账号**：15577305913
- **密码**：passwor

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
│   ├── nginx.conf
│   └── package.json
├── deploy/              # 部署配置
│   ├── docker-compose.yml
│   ├── deploy.sh        # 一键部署脚本
│   ├── undeploy.sh      # 卸载脚本
│   └── README.md        # 部署说明
├── start-backend.sh     # 后端启动脚本
└── start-frontend.sh    # 前端启动脚本
```

## 核心功能

### 1. 设备管理
- **绑定设备**：输入 IMEI 码和设备名称
- **设备列表**：显示设备状态、电量、最后位置
- **设备操作**：重命名、解绑

### 2. 地图定位
- **实时位置**：显示设备当前坐标
- **轨迹回放**：播放/暂停/速度调节
- **轨迹摘要**：采样点、报警次数统计

### 3. 电子围栏
- **创建围栏**：中心点 + 半径
- **围栏状态**：围栏内/围栏外
- **越界报警**：自动触发通知

### 4. 报警系统
- **报警类型**：防拆、跌倒、静止、低电量、SOS、围栏越界
- **通知渠道**：应用内、SMS、微信
- **报警记录**：历史报警查询

### 5. 管理员功能
- **用户管理**：查看、修改角色、删除
- **设备管理**：平台所有设备
- **统计报表**：用户、设备、报警、通知统计

## 部署指南

### 环境要求
- Docker 20.10+
- Docker Compose 1.29+

### 部署步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/aajj1314/ananProject.git
   cd ananProject
   ```

2. **一键部署**
   ```bash
   cd deploy
   ./deploy.sh start
   ```

3. **验证服务**
   - 前端：http://localhost:8081
   - 后端：http://localhost:8000/health

4. **管理命令**
   ```bash
   ./deploy.sh status    # 查看状态
   ./deploy.sh stop      # 停止服务
   ./deploy.sh restart   # 重启服务
   ./deploy.sh logs      # 查看日志
   ```

### 生产环境配置

修改 `deploy/.env` 文件：

```env
# 生产环境配置
APP_ENV=production
DEBUG=false
JWT_SECRET=your-secure-random-secret
DATABASE_URL=mysql+aiomysql://user:password@db:3306/elderly_care
```

## 安全注意事项

1. **JWT 密钥**：生产环境必须修改为强随机密钥
2. **密码哈希**：使用 bcrypt 算法
3. **速率限制**：防止暴力破解
4. **CORS 配置**：仅允许信任的域名
5. **数据备份**：定期备份数据库

## 常见问题

### Q: 如何创建管理员账号？
A: 系统默认创建管理员账号：15577305913 / passwor

### Q: 如何集成真实地图？
A: 在 `frontend/.env` 配置：
```env
VITE_MAP_PROVIDER=amap  # 或 baidu
VITE_MAP_API_KEY=your-api-key
```

### Q: 如何配置 SMS/微信通知？
A: 在 `.env` 中配置相应的 API 密钥和参数

### Q: 数据存储在哪里？
A: 默认使用 SQLite，生产环境建议使用 MySQL

## 技术支持

如遇到问题，请检查：
1. 服务状态：`./deploy.sh status`
2. 日志信息：`./deploy.sh logs`
3. 环境配置：检查 `.env` 文件
4. 网络连接：确保端口未被占用

## 许可证

本项目为老人防丢鞋垫系统的完整实现。