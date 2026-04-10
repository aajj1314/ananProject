# Docker 部署指南

## 快速开始（推荐）

### 一键启动

```bash
cd deploy
cp .env.example .env
# 编辑 .env 设置 JWT_SECRET
docker-compose up -d
```

### 访问服务

- **前端**: http://localhost:8080
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 完整部署步骤

### 1. 准备环境配置

```bash
cd deploy

# 复制环境配置模板
cp .env.example .env

# 编辑环境配置（重要：修改 JWT_SECRET）
# 使用强密码作为 JWT_SECRET
```

### 2. 构建并启动服务

```bash
# 首次构建并启动（后台运行）
docker-compose up -d --build

# 或仅启动（已构建过）
docker-compose up -d
```

### 3. 查看服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 停止服务

```bash
# 停止服务但保留数据
docker-compose down

# 停止服务并删除数据卷（谨慎使用！）
docker-compose down -v
```

---

## 服务说明

### 包含的服务

| 服务 | 说明 | 端口 |
|------|------|------|
| `frontend` | Nginx + Vue 3 前端 | 8080 |
| `backend` | FastAPI 后端 | 8000 |
| `redis` | Redis 缓存（可选） | - |

### 数据持久化

- 后端数据库: `backend_data` volume
- Redis 数据: `redis_data` volume

---

## 配置说明

### 环境变量

关键配置项在 `deploy/.env` 中：

| 配置项 | 说明 | 必需 |
|--------|------|------|
| `JWT_SECRET` | JWT 签名密钥，生产环境必须修改 | ✅ |
| `APP_ENV` | 运行环境 (development/production) | - |
| `DEBUG` | 是否开启调试模式 | - |
| `DATABASE_URL` | 数据库连接字符串 | - |
| `REDIS_URL` | Redis 连接字符串 | - |

### 数据库

默认使用 SQLite（无需额外配置），适合中小规模部署。

如需使用 MySQL：

```env
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/elderly_care
```

---

## 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务健康状态
docker-compose ps

# 手动测试健康端点
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/detailed
```

---

## 故障排除

### 问题：端口被占用

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8081:80"    # 前端改为 8081
  - "8001:8000"  # 后端改为 8001
```

### 问题：容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 重启单个服务
docker-compose restart backend
```

### 问题：前端无法连接后端

检查：
1. 后端容器是否正常运行: `docker-compose ps`
2. 后端日志: `docker-compose logs backend`
3. 手动测试后端: `curl http://localhost:8000/health`

---

## 生产环境建议

1. **修改 JWT_SECRET** 为强随机字符串
2. **使用 HTTPS** (配置 SSL 证书)
3. **定期备份** 数据卷
4. **配置日志** 轮转和收集
5. **设置资源限制** 在 docker-compose.yml 中
6. **使用外部数据库** (MySQL/PostgreSQL)

---

## 开发模式 vs 生产模式

| 特性 | 开发模式 | 生产模式 (Docker) |
|------|---------|------------------|
| 热重载 | ✅ | ❌ |
| 调试日志 | ✅ | 可选 |
| SQLite | ✅ | ✅ (或 MySQL) |
| Redis | 可选 | ✅ |
| 数据持久化 | 本地文件 | Docker volumes |

---

## 下一步

部署成功后：

1. 访问 http://localhost:8080 查看前端
2. 访问 http://localhost:8000/docs 查看 API 文档
3. 注册一个测试用户
4. 开始使用系统！
