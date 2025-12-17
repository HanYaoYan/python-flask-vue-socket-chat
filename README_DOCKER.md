# Docker 一键启动指南

本项目提供完整的 Docker 部署方案，**无需安装 Node.js 或 Python**，只需 Docker 即可运行整个应用。

## 🚀 快速开始

### Windows 用户

1. **确保 Docker Desktop 已启动**

2. **双击运行 `启动.bat`**

   或在命令行执行：
   ```cmd
   启动.bat
   ```

3. **等待服务启动完成**
   - 首次启动需要下载镜像，约 3-8 分钟
   - 前端构建 npm 依赖可能需要额外时间
   - 请耐心等待，直到所有服务状态显示为 "Up"

4. **访问应用**
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:9000/api/health

### Linux/macOS 用户

1. **确保 Docker 和 Docker Compose 已安装并运行**

2. **给启动脚本添加执行权限**
   ```bash
   chmod +x 启动.sh 停止.sh
   ```

3. **运行启动脚本**
   ```bash
   ./启动.sh
   ```

4. **等待服务启动完成**
   - 首次启动需要下载镜像，约 3-8 分钟
   - 前端构建 npm 依赖可能需要额外时间
   - 请耐心等待，直到所有服务状态显示为 "Up"

5. **访问应用**
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:9000/api/health

### 手动启动（所有平台）

```bash
docker-compose -f docker-compose.full.yml up -d --build
```

## 📋 服务说明

启动后，以下服务会自动运行：

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| MySQL | chat_mysql | 3306 | 数据库 |
| Redis | chat_redis | 6379 | 缓存 |
| Flask 后端 | chat_app | 9000 | API 服务 |
| Vue 前端 | chat_frontend | 5173 | 前端开发服务器（Node.js） |

> **注意**：前端服务会在 Docker 容器中运行 Node.js，首次构建需要安装 npm 依赖，可能需要 2-5 分钟。

## 🔧 常用命令

### 查看服务状态

```bash
docker-compose -f docker-compose.full.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.full.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.full.yml logs -f app
docker-compose -f docker-compose.full.yml logs -f frontend
```

### 停止服务

**Windows:**
```cmd
停止.bat
```

**Linux/macOS:**
```bash
./停止.sh
```

**手动停止:**
```bash
docker-compose -f docker-compose.full.yml down
```

### 重启服务

```bash
docker-compose -f docker-compose.full.yml restart
```

### 停止并删除所有数据（谨慎使用）

```bash
docker-compose -f docker-compose.full.yml down -v
```

## 🔍 验证服务

### 检查后端健康

```bash
curl http://localhost:9000/api/health
```

应返回：
```json
{"database":"connected","redis":"connected","status":"ok"}
```

### 检查前端

打开浏览器访问：http://localhost:5173

应该看到登录页面。

## 📦 打包给其他人

### 方式一：直接分发项目文件夹

1. **确保包含以下文件：**
   - `docker-compose.full.yml`
   - `启动.bat` / `启动.sh`
   - `停止.bat` / `停止.sh`
   - 所有源代码文件

2. **打包压缩：**
   ```bash
   # 排除不必要的文件
   zip -r chat-app.zip . -x "node_modules/*" "__pycache__/*" ".git/*"
   ```

3. **接收者只需要：**
   - 解压文件
   - 安装 Docker Desktop
   - 运行 `启动.bat` 或 `启动.sh`

### 方式二：构建镜像并分发

1. **保存镜像：**
   ```bash
   docker save chat-app:latest > chat-app-backend.tar
   docker save chat-frontend:latest > chat-app-frontend.tar
   ```

2. **接收者加载镜像：**
   ```bash
   docker load < chat-app-backend.tar
   docker load < chat-app-frontend.tar
   ```

## ⚙️ 环境变量配置

如果需要修改配置，可以创建 `.env` 文件：

```env
# 数据库配置
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=chat_db

# 应用密钥（生产环境请修改）
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

## 🐛 故障排查

### 端口被占用

如果端口 5173、9000、3306、6379 被占用，可以：

1. **修改端口映射**（编辑 `docker-compose.full.yml`）：
   ```yaml
   ports:
     - "5174:5173"  # 前端改为 5174
     - "9001:9000"  # 后端改为 9001
   ```

2. **或停止占用端口的服务**

### 服务启动失败

1. **查看日志：**
   ```bash
   # 查看所有服务日志
   docker-compose -f docker-compose.full.yml logs
   
   # 查看前端服务日志（前端构建问题）
   docker-compose -f docker-compose.full.yml logs frontend
   
   # 查看后端服务日志
   docker-compose -f docker-compose.full.yml logs app
   ```

2. **检查 Docker 资源：**
   - 确保 Docker 有足够的内存（建议 4GB+）
   - 确保磁盘空间充足

3. **前端镜像拉取失败（网络问题）：**
   如果 `node:18-alpine` 镜像拉取失败，可以：
   - 配置 Docker 镜像加速器（推荐）
   - 或使用本地 Node.js 启动前端（见下方说明）

4. **重新构建：**
   ```bash
   docker-compose -f docker-compose.full.yml up -d --build --force-recreate
   ```

### 前端 Docker 镜像拉取失败（备用方案）

如果因为网络问题无法拉取前端 Docker 镜像，可以使用本地 Node.js 启动前端：

1. **只启动后端服务：**
   ```bash
   docker-compose up -d
   ```

2. **本地启动前端：**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### 前端无法访问后端

1. **检查后端是否运行：**
   ```bash
   docker-compose -f docker-compose.full.yml ps app
   ```

2. **检查后端日志：**
   ```bash
   docker-compose -f docker-compose.full.yml logs app
   ```

3. **测试后端 API：**
   ```bash
   curl http://localhost:9000/api/health
   ```

## 📚 更多信息

- **只启动后端（不使用 Docker 前端）：** 使用 `docker-compose.yml`
- **项目结构说明：** 查看 `docs/PROJECT_STRUCTURE.md`

## ✅ 优势

- ✅ **零配置**：无需安装 Node.js、Python、MySQL、Redis
- ✅ **环境一致**：所有人使用相同的环境，避免版本问题
- ✅ **易于分发**：打包项目文件夹即可
- ✅ **隔离运行**：不污染本地环境
- ✅ **一键启动**：运行脚本即可启动所有服务

