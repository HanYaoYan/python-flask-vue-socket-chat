# Docker 部署指南

## 使用 Docker Compose 一键启动（推荐）

### 快速启动

```bash
# 启动所有服务（MySQL + Redis + Flask 应用）
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 查看所有服务状态
docker-compose ps

# 停止所有服务
docker-compose down

# 停止并删除数据卷（会删除数据库数据）
docker-compose down -v
```

### 服务说明

Docker Compose 会启动三个服务：

1. **MySQL 8.0** (端口 3306)
   - 数据库名称: `chat_db`
   - 默认密码: `password`（可通过环境变量修改）

2. **Redis 6.0** (端口 6379)
   - 数据持久化: 开启 AOF

3. **Flask 应用** (端口 9000)
   - API 地址: http://localhost:9000
   - 健康检查: http://localhost:9000/api/health

### 环境变量配置

可以在项目根目录创建 `.env` 文件来自定义配置：

```env
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=chat_db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

然后在 `docker-compose.yml` 中会自动读取这些变量。

### 首次启动步骤

1. **启动服务**
   ```bash
   docker-compose up -d
   ```

2. **等待数据库初始化完成**（约 10-30 秒）
   ```bash
   docker-compose logs -f mysql
   ```
   看到 `ready for connections` 表示 MySQL 已就绪

3. **初始化数据库表**
   ```bash
   # 方法一：进入容器执行
   docker-compose exec app python3 init_db.py
   
   # 方法二：应用会自动创建表（如果 app.py 中有 init_db 调用）
   ```

4. **检查服务健康状态**
   ```bash
   curl http://localhost:9000/api/health
   ```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f app      # Flask 应用
docker-compose logs -f mysql    # MySQL
docker-compose logs -f redis    # Redis
```

### 数据库管理

#### 进入 MySQL 容器

```bash
docker-compose exec mysql mysql -uroot -ppassword chat_db
```

#### 备份数据库

```bash
docker-compose exec mysql mysqldump -uroot -ppassword chat_db > backup.sql
```

#### 恢复数据库

```bash
docker-compose exec -T mysql mysql -uroot -ppassword chat_db < backup.sql
```

### Redis 管理

#### 进入 Redis 容器

```bash
docker-compose exec redis redis-cli
```

#### 查看在线用户

```bash
docker-compose exec redis redis-cli SCARD online_users
docker-compose exec redis redis-cli SMEMBERS online_users
```

### 仅启动数据库服务（用于本地开发）

如果你想在本地运行 Flask 应用，但使用 Docker 的数据库：

```bash
# 只启动 MySQL 和 Redis
docker-compose up -d mysql redis

# 在本地运行 Flask 应用
python app.py
```

记得在 `.env` 文件中配置：
```env
MYSQL_HOST=localhost
REDIS_HOST=localhost
```

### 常见问题

#### 1. 端口冲突

如果 3306、6379 或 9000 端口已被占用，可以修改 `docker-compose.yml`：

```yaml
mysql:
  ports:
    - "3307:3306"  # 改为 3307:3306
```

#### 2. 数据库连接失败

确保等待 MySQL 完全启动后再启动应用。Docker Compose 已配置了健康检查和依赖关系。

#### 3. 数据持久化

数据库数据存储在 Docker 卷中，即使容器删除，数据也不会丢失（除非使用 `docker-compose down -v`）。

查看卷：
```bash
docker volume ls
```

#### 4. 重新构建镜像

如果修改了代码或依赖，需要重新构建：

```bash
docker-compose build
docker-compose up -d
```

#### 5. 清理所有数据

```bash
# 停止并删除容器、网络、数据卷
docker-compose down -v

# 删除镜像
docker-compose rm -f
docker rmi python-flask-vue-socket-chat_app
```

### 生产环境建议

1. **修改默认密码**：在 `.env` 文件中设置强密码
2. **配置防火墙**：只开放必要的端口
3. **使用反向代理**：建议使用 Nginx 作为反向代理
4. **启用 HTTPS**：配置 SSL 证书
5. **数据备份**：定期备份 MySQL 数据
6. **监控日志**：配置日志收集和监控

### Docker 命令速查

```bash
# 启动
docker-compose up -d

# 停止
docker-compose stop

# 重启
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec [service_name] /bin/bash

# 重新构建
docker-compose build

# 清理
docker-compose down -v
```

