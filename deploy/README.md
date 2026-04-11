# 智慧养老鞋垫平台 - 部署指南

## 部署要求

| 依赖 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Docker | 20.10+ | 24.0+ |
| Docker Compose | V2 (内置) | 最新 |
| 磁盘空间 | 2GB+ | 5GB+ |
| 内存 | 1GB+ | 2GB+ |

> Docker Compose V2 已内置在 Docker Desktop 和新版 Docker Engine 中，无需单独安装。

## 快速开始

### 一键部署（推荐）

```bash
cd deploy
chmod +x deploy.sh undeploy.sh
./deploy.sh start
```

部署成功后访问：
- 前端：http://localhost:8081
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

默认管理员账号：
- 手机号：15577305913
- 密码：passwor

### 手动部署

```bash
cd deploy

# 直接使用 docker compose 启动（使用默认配置）
docker compose --profile prod up -d --build

# 或者自定义环境变量后启动
export JWT_SECRET=$(openssl rand -hex 32)
export ADMIN_PHONE=15577305913
export ADMIN_PASSWORD=passwor
docker compose --profile prod up -d --build
```

## 配置说明

### 环境变量

所有配置都有合理的默认值，无需额外配置即可运行。以下变量可通过环境变量或 `.env` 文件覆盖：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `JWT_SECRET` | 自动生成 | JWT 签名密钥，生产环境务必修改 |
| `JWT_EXPIRE_MINUTES` | 1440 | Token 过期时间（分钟） |
| `ADMIN_PHONE` | 15577305913 | 管理员手机号 |
| `ADMIN_PASSWORD` | passwor | 管理员密码 |
| `BACKEND_PORT` | 8000 | 后端服务端口 |
| `FRONTEND_PORT` | 8081 | 前端服务端口 |

### 自定义配置

方式一：创建 `.env` 文件

```bash
cd deploy
cat > .env << 'EOF'
JWT_SECRET=your-secure-random-string-here
ADMIN_PHONE=13800138000
ADMIN_PASSWORD=YourSecurePassword123
BACKEND_PORT=8000
FRONTEND_PORT=8081
EOF
```

方式二：通过环境变量

```bash
export JWT_SECRET=$(openssl rand -hex 32)
export ADMIN_PASSWORD=YourSecurePassword123
./deploy.sh start
```

### Profiles 说明

docker-compose.yml 使用 profiles 区分环境：

- `prod` - 生产模式（默认）
- `dev` - 开发模式

```bash
# 生产模式
docker compose --profile prod up -d

# 开发模式
docker compose --profile dev up -d
```

## 部署脚本使用

### deploy.sh

```bash
./deploy.sh start     # 构建并启动所有服务
./deploy.sh stop      # 停止所有服务
./deploy.sh restart   # 重启所有服务
./deploy.sh status    # 查看服务状态和健康检查
./deploy.sh logs      # 查看所有服务日志
./deploy.sh logs backend   # 查看后端日志
./deploy.sh logs frontend  # 查看前端日志
./deploy.sh logs redis     # 查看Redis日志
```

### undeploy.sh

```bash
./undeploy.sh         # 交互式卸载，可选择保留数据
```

卸载脚本会依次询问：
1. 是否停止服务
2. 是否删除数据卷（数据库和缓存数据）
3. 是否删除 Docker 镜像
4. 是否删除 .env 配置文件

## 服务架构

```
                    +------------------+
                    |   用户浏览器      |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Nginx (前端)    |  :8081
                    |   Vue 3 SPA      |
                    +--------+---------+
                             | /api/ 代理
                    +--------v---------+
                    |   FastAPI (后端)  |  :8000
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Redis (缓存)    |
                    +------------------+
                             |
                    +--------v---------+
                    |   SQLite (数据库) |
                    |   (Docker Volume) |
                    +------------------+
```

## 数据持久化

| 数据 | Docker Volume | 说明 |
|------|--------------|------|
| SQLite 数据库 | `backend_data` | 用户、设备、围栏等业务数据 |
| Redis 缓存 | `redis_data` | 会话缓存、限流计数 |

数据卷位置：`/var/lib/docker/volumes/deploy_xxx/_data`

### 数据备份

```bash
# 备份数据库
docker cp elderly-care-backend:/app/data/elderly_insole.db ./backup_$(date +%Y%m%d).db

# 备份整个数据卷
docker run --rm -v deploy_backend_data:/data -v $(pwd):/backup alpine tar czf /backup/backend_data_$(date +%Y%m%d).tar.gz -C /data .
```

### 数据恢复

```bash
# 恢复数据库
docker cp ./backup_20240101.db elderly-care-backend:/app/data/elderly_insole.db
docker restart elderly-care-backend
```

## 常见问题

### 1. 端口被占用

修改环境变量后重新启动：

```bash
export BACKEND_PORT=8001
export FRONTEND_PORT=8082
./deploy.sh restart
```

### 2. 前端无法连接后端

前端通过 Nginx 反向代理访问后端，使用 Docker 内部网络通信（service name: `elderly-care-backend`），不依赖外部网络。

排查步骤：
```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查容器网络
docker network inspect deploy_app-network

# 查看后端日志
./deploy.sh logs backend
```

### 3. 容器启动失败

```bash
# 查看详细日志
docker compose --profile prod logs backend

# 检查容器状态
docker compose --profile prod ps -a

# 重建容器
docker compose --profile prod up -d --build --force-recreate
```

### 4. 忘记管理员密码

删除数据库卷并重新启动，系统会自动创建默认管理员：

```bash
docker compose --profile prod down -v
./deploy.sh start
```

### 5. Docker Compose V1 vs V2

部署脚本自动检测并适配两种版本。推荐使用 V2（`docker compose`），V1（`docker-compose`）也可用但已停止维护。

### 6. 数据库迁移

系统启动时会自动检测并添加缺失的列，无需手动迁移。如需完全重建：

```bash
docker compose --profile prod down -v  # 删除数据卷
./deploy.sh start                       # 重新启动
```

## 生产环境安全建议

1. **修改 JWT_SECRET** - 使用强随机字符串：`openssl rand -hex 32`
2. **修改管理员密码** - 使用强密码
3. **配置 HTTPS** - 使用 Nginx 反向代理 + Let's Encrypt 证书
4. **限制端口暴露** - 仅暴露前端端口，后端端口不对外
5. **定期备份** - 设置定时任务备份数据库
6. **监控日志** - 配置日志收集和告警
7. **资源限制** - docker-compose.yml 已配置内存限制，根据实际需求调整
