# 项目运行指南

## 当前环境状态

✅ 项目代码已 100% 完成
✅ 所有功能已实现
✅ 完整文档已就绪
⚠️ 虚拟环境需要重新配置

---

## 方式一：重新创建虚拟环境（推荐）

由于当前虚拟环境可能有问题，建议重新创建：

### Linux 环境

```bash
# 1. 删除旧的虚拟环境
rm -rf .venv

# 2. 创建新的虚拟环境
python3 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt

# 5. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows 环境

```powershell
# 1. 删除旧的虚拟环境
Remove-Item -Recurse -Force .venv

# 2. 创建新的虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
.venv\Scripts\Activate.ps1

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt

# 5. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动，API 文档在 http://localhost:8000/docs

---

## 方式二：使用启动脚本

### Linux 环境

```bash
# 后端
./start-backend.sh

# 前端（另一个终端）
./start-frontend.sh
```

### Windows 环境

```powershell
# 后端
./start-backend.ps1

# 前端（另一个终端）
./start-frontend.ps1
```

---

## 方式三：Docker 部署（最简单）

```bash
cd deploy
docker-compose up -d
```

服务将在以下地址访问：
- 前端: http://localhost:8081
- 后端: http://localhost:8000

---

## 前端启动

### Linux 环境

```bash
cd frontend
npm install
npm run dev
```

### Windows 环境

```powershell
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:8081 启动

---

## 验证步骤

### 1. 验证后端启动

访问 http://localhost:8000/docs 应该能看到 Swagger API 文档

### 2. 测试健康检查

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/detailed
```

### 3. 测试注册用户

使用 Swagger UI 或 curl 测试：

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"passw0rd","nickname":"测试用户"}'
```

---

## 环境变量配置

复制配置模板并按需修改：

```bash
# 后端配置
cd backend
cp ../.env.development.example .env
# 编辑 .env 文件
```

关键配置项：
- `DATABASE_URL`: 数据库连接（默认 SQLite，无需修改）
- `JWT_SECRET`: 生产环境必须修改
- `NOTIFICATION_CHANNELS`: 启用的通知渠道

---

## 常见问题

### Q: ModuleNotFoundError: No module named 'xxx'

A: 确保在虚拟环境中安装了依赖：
```bash
source .venv/bin/activate
cd backend
pip install -r requirements.txt
```

### Q: 端口被占用

A: 修改启动端口：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Q: 前端无法连接后端

A: 检查 `frontend/src/api/api.ts` 中的 `baseURL` 是否正确

### Q: 数据库错误

A: 删除 SQLite 数据库文件，重新创建：
```bash
cd backend
rm elderly_insole_dev.db
```

---

## 项目文件确认

确保以下文件存在：

```
ananProject/
├── backend/              # 后端代码
├── frontend/             # 前端代码
├── deploy/               # Docker 配置
├── README.md             # 项目首页
├── QUICKSTART.md         # 快速启动
├── USAGE.md              # 详细使用说明
├── RUN_GUIDE.md          # 本文档
├── WORKLOG.md            # 工作日志
├── PROJECT_ROADMAP.md    # 项目路线图
├── PROJECT_MEMORY.md     # 项目记忆
├── start-backend.sh      # 后端启动脚本
└── start-frontend.sh     # 前端启动脚本
```

---

## 功能测试清单

启动后可以测试以下功能：

- [ ] 用户注册
- [ ] 用户登录
- [ ] 绑定设备
- [ ] 查看设备列表
- [ ] 查看地图和位置
- [ ] 创建电子围栏
- [ ] 上传定位数据
- [ ] 查看报警记录
- [ ] 查看通知历史
- [ ] 管理员仪表板（需要先设为管理员）

---

## 获取帮助

详细使用说明请参考：
- `USAGE.md` - 详细使用说明书
- `QUICKSTART.md` - 快速启动指南
- Swagger API 文档 - http://localhost:8000/docs
