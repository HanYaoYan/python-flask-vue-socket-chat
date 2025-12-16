# 部署指南

## 本地开发环境部署

### 前置要求

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Node.js 16+**
   ```bash
   node --version
   ```

3. **MySQL 8.0+**
   - 下载安装：https://dev.mysql.com/downloads/mysql/
   - 或使用 Docker：`docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql:8.0`

4. **Redis 6.0+**
   - 下载安装：https://redis.io/download
   - 或使用 Docker：`docker run -d -p 6379:6379 redis:6.0-alpine`

### 步骤

#### 1. 克隆并进入项目目录

```bash
cd python-flask-vue-socket-chat
```

#### 2. 配置环境变量

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接信息。

#### 3. 创建 MySQL 数据库

```sql
CREATE DATABASE chat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

如果遇到 MySQL 客户端安装问题：

**Windows:**
- 下载 MySQL Connector/C 或使用 conda 安装

**Linux:**
```bash
sudo apt-get install default-libmysqlclient-dev  # Ubuntu/Debian
sudo yum install mysql-devel  # CentOS/RHEL
```

**macOS:**
```bash
brew install mysql-client
```

#### 5. 初始化数据库表

```bash
python init_db.py
```

或直接运行应用，会自动创建表：
```bash
python app.py
```

#### 6. 启动后端服务

```bash
python app.py
```

后端将在 `http://localhost:9000` 启动。

#### 7. 安装前端依赖

```bash
cd frontend
npm install
```

#### 8. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动。

#### 9. 启动 Electron 桌面应用

```bash
npm run electron:dev
```

## Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

访问：
- API: http://localhost:9000
- 健康检查: http://localhost:9000/api/health

### 仅启动数据库服务

```bash
# 启动 MySQL 和 Redis
docker-compose up -d mysql redis

# 查看状态
docker-compose ps
```

## 生产环境部署

### 后端部署

1. **使用 Gunicorn + Eventlet**

```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:9000 app:app
```

2. **使用 Nginx 反向代理**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 前端构建

```bash
cd frontend
npm run build
```

### Electron 桌面应用打包

#### Windows
```bash
npm run electron:build:win
```

#### macOS
```bash
npm run electron:build:mac
```

#### Linux
```bash
npm run electron:build:linux
```

打包产物在 `frontend/dist-electron` 目录。

## 常见问题

### 1. MySQL 连接失败

**错误**: `Can't connect to MySQL server`

**解决**:
- 检查 MySQL 服务是否启动
- 检查 `.env` 中的数据库配置
- 检查防火墙设置
- 确认数据库已创建

### 2. Redis 连接失败

**错误**: `Connection refused`

**解决**:
- 检查 Redis 服务是否启动: `redis-cli ping`
- 检查 `.env` 中的 Redis 配置
- 检查防火墙设置

### 3. 前端 Socket.IO 连接失败

**错误**: `WebSocket connection failed`

**解决**:
- 确认后端服务运行在正确端口
- 检查 CORS 配置
- 检查防火墙是否阻止 WebSocket 连接

### 4. 数据库表创建失败

**错误**: `Table already exists` 或 `Access denied`

**解决**:
- 删除现有表或使用新数据库
- 检查数据库用户权限
- 确认数据库字符集为 `utf8mb4`

### 5. Python 依赖安装失败

**错误**: `Failed building wheel for...`

**解决**:
- 更新 pip: `pip install --upgrade pip`
- 安装编译工具（Windows: Visual C++, Linux: build-essential）
- 使用 conda 环境

## 性能调优

### MySQL 优化

```sql
-- 添加索引
ALTER TABLE messages ADD INDEX idx_room_created (room_id, created_at);
ALTER TABLE messages ADD INDEX idx_sender_created (sender_id, created_at);
```

### Redis 优化

在 `redis.conf` 中：
```conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Flask 应用优化

使用多进程模式：
```bash
gunicorn --workers 4 --worker-class eventlet -w 1 --bind 0.0.0.0:9000 app:app
```

## 监控和维护

### 健康检查

```bash
curl http://localhost:9000/api/health
```

### 查看在线用户数

```bash
redis-cli SCARD online_users
```

### 数据库备份

```bash
mysqldump -u root -p chat_db > backup_$(date +%Y%m%d).sql
```

### 日志查看

应用日志输出到控制台，生产环境建议配置日志文件：
```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

