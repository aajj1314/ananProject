# 老人防丢鞋垫系统 - 部署指南

## 目录

- [部署概述](#部署概述)
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [配置说明](#配置说明)
- [管理命令](#管理命令)
- [服务架构](#服务架构)
- [数据管理](#数据管理)
- [常见问题](#常见问题)
- [安全建议](#安全建议)

## 部署概述

本部署方案使用 Docker Compose 实现完整的容器化部署，包含以下服务：

- **前端**：Vue 3 + TypeScript + Nginx
- **后端**：FastAPI + SQLAlchemy
- **Redis**：缓存和速率限制

## 环境要求

- Docker 20.10 或更高版本
- Docker Compose 1.29 或更高版本
- 至少 1GB 内存
- 至少 10GB 磁盘空间

## 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/aajj1314/ananProject.git
cd ananProject
```

### 2. 进入部署目录

```bash
cd deploy
```

### 3. 一键部署

```bash
chmod +x deploy.sh undeploy.sh
./deploy.sh start
```

### 4. 验证服务

部署完成后，服务将在以下地址运行：

- **前端应用**：http://localhost:8081
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

### 5. 登录系统

- **管理员账号**：15577305913
- **密码**：passwor

## 配置说明

### 环境变量

`docker-compose.yml` 文件包含以下可配置的环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `FRONTEND_PORT` | 8081 | 前端服务端口 |
| `BACKEND_PORT` | 8000 | 后端服务端口 |
| `ADMIN_PHONE` | 15577305913 | 默认管理员手机号 |
| `ADMIN_PASSWORD` | passwor | 默认管理员密码 |
| `JWT_SECRET` | elderly-care-default-jwt-secret | JWT 密钥 |
| `DATABASE_URL` | sqlite+aiosqlite:///./elderly_insole.db | 数据库连接 |
| `REDIS_URL` | redis://redis:6379/0 | Redis 连接 |

### 自定义配置

如需自定义配置，可以：

1. **修改 docker-compose.yml**：直接编辑文件中的环境变量
2. **使用环境变量**：在启动前设置环境变量覆盖默认值

## 管理命令

### 部署脚本

`deploy.sh` 脚本提供以下命令：

| 命令 | 说明 |
|------|------|
| `./deploy.sh start` | 启动所有服务 |
| `./deploy.sh stop` | 停止所有服务 |
| `./deploy.sh restart` | 重启所有服务 |
| `./deploy.sh status` | 查看服务状态 |
| `./deploy.sh logs` | 查看服务日志 |

### 卸载脚本

`undeploy.sh` 脚本用于完全清理部署：

```bash
./undeploy.sh
```

选项：
- 停止所有服务
- 可选删除数据卷
- 可选删除 Docker 镜像
- 清理 Docker 网络

## 服务架构

```
┌─────────────────┐
│   客户端浏览器   │
└────────┬────────┘
         │
┌────────▼────────┐
│    Nginx (8081)  │
└────────┬────────┘
         │
┌────────▼────────┐     ┌───────────────┐
│  前端 (Vue 3)   │────>│  后端 (FastAPI) │
└─────────────────┘     └────────┬──────┘
                                 │
                       ┌─────────┴─────────┐
                       │                   │
               ┌───────▼───────┐   ┌──────▼──────┐
               │  SQLite/MySQL  │   │   Redis     │
               └───────────────┘   └────────────┘
```

## 数据管理

### 数据存储

- **数据库**：默认使用 SQLite 数据库文件 (`backend/elderly_insole.db`)
- **缓存**：Redis 用于速率限制和缓存

### 数据备份

#### SQLite 备份

```bash
# 备份数据库
docker cp $(docker ps -qf "name=elderly-care-backend"):/app/elderly_insole.db ./backup.db

# 恢复数据库
docker cp ./backup.db $(docker ps -qf "name=elderly-care-backend"):/app/elderly_insole.db
```

#### MySQL 备份

如果使用 MySQL，使用 `mysqldump` 进行备份：

```bash
docker exec -t mysql_container mysqldump -u root -p password database_name > backup.sql
```

## 常见问题

### Q: 部署失败怎么办？
A: 检查日志输出：`./deploy.sh logs`

### Q: 端口被占用怎么办？
A: 修改 `docker-compose.yml` 中的 `FRONTEND_PORT` 和 `BACKEND_PORT`

### Q: 服务启动后无法访问？
A: 检查防火墙设置，确保端口已开放

### Q: 如何更新代码？
A:
1. 停止服务：`./deploy.sh stop`
2. 拉取最新代码：`git pull`
3. 重新部署：`./deploy.sh start`

### Q: 如何查看详细日志？
A:
```bash
# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend
```

## 安全建议

### 生产环境配置

1. **修改 JWT 密钥**：
   ```bash
   # 生成强随机密钥
   openssl rand -hex 32
   ```

2. **修改默认密码**：
   ```yaml
   # docker-compose.yml
   environment:
     ADMIN_PASSWORD: your-secure-password
   ```

3. **使用 HTTPS**：
   - 配置 Nginx 支持 SSL
   - 使用 Let's Encrypt 证书

4. **网络隔离**：
   - 确保容器网络与外部隔离
   - 仅暴露必要的端口

5. **定期更新**：
   - 定期更新 Docker 镜像
   - 定期更新依赖包

### 监控建议

- **健康检查**：定期访问 `/health` 端点
- **日志监控**：配置日志收集系统
- **告警机制**：设置服务异常告警

## 技术支持

如遇到问题，请按照以下步骤排查：

1. **检查服务状态**：`./deploy.sh status`
2. **查看日志**：`./deploy.sh logs`
3. **检查网络**：确保端口未被占用
4. **检查配置**：验证环境变量设置
5. **重启服务**：`./deploy.sh restart`

如果问题仍未解决，请参考项目文档或联系技术支持。