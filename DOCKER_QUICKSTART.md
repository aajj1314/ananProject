# Docker 一键启动指南

## 🚀 三个命令启动项目

```bash
# 1. 进入部署目录
cd deploy

# 2. 复制环境配置
cp .env.example .env

# 3. 启动所有服务
docker-compose up -d
```

## 📱 访问地址

启动成功后访问：

| 服务 | 地址 |
|------|------|
| 🌐 前端 | http://localhost:8080 |
| 🔧 后端 API | http://localhost:8000 |
| 📚 API 文档 | http://localhost:8000/docs |

---

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

## ✅ 验证部署

```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 应该返回: {"status":"ok",...}
```

---

## 📖 详细文档

- 详细部署指南: [deploy/README.md](./deploy/README.md)
- 项目使用说明: [USAGE.md](./USAGE.md)
- 快速启动指南: [QUICKSTART.md](./QUICKSTART.md)

---

## ⚠️ 生产环境注意

部署前必须修改 `deploy/.env` 中的：

```env
JWT_SECRET=你的强随机密钥
```

---

## 🎉 完成！

项目现在已通过 Docker 容器化运行！
