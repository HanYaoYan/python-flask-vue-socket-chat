# Docker 构建方式说明

本项目提供了两种 Dockerfile 和两种 docker-compose 配置，您可以根据网络环境选择使用。

## 文件说明

### Dockerfile 文件

1. **Dockerfile**（默认，使用官方镜像源）
   - Python 基础镜像：`python:3.8-slim`（Docker Hub）
   - PyPI 包源：官方 PyPI
   - 适用于：可正常访问 Docker Hub 的网络环境

2. **Dockerfile.cn**（国内镜像源）
   - Python 基础镜像：`registry.cn-hangzhou.aliyuncs.com/library/python:3.8-slim`（阿里云）
   - PyPI 包源：清华大学镜像源
   - 适用于：中国大陆或无法访问 Docker Hub 的环境

### Docker Compose 文件

1. **docker-compose.yml**（默认配置）
   - 使用 `Dockerfile`
   - MySQL 镜像：`mysql:8.0`（Docker Hub）
   - Redis 镜像：`redis:6.0-alpine`（Docker Hub）

2. **docker-compose.cn.yml**（国内镜像配置）
   - 使用 `Dockerfile.cn`
   - MySQL 镜像：`registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0`（阿里云）
   - Redis 镜像：`registry.cn-hangzhou.aliyuncs.com/library/redis:6.0-alpine`（阿里云）

## 使用方法

### 方式一：使用官方镜像源（默认）

**适用场景**：网络可以正常访问 Docker Hub

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 仅构建
docker-compose build

# 仅启动（不构建）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二：使用国内镜像源

**适用场景**：在中国大陆或无法访问 Docker Hub

```bash
# 构建并启动所有服务
docker-compose -f docker-compose.cn.yml up -d --build

# 仅构建
docker-compose -f docker-compose.cn.yml build

# 仅启动（不构建）
docker-compose -f docker-compose.cn.yml up -d

# 查看日志
docker-compose -f docker-compose.cn.yml logs -f

# 停止服务
docker-compose -f docker-compose.cn.yml down
```

### 方式三：混合使用（推荐）

**场景**：已配置 Docker 镜像加速器，但仍希望某些服务使用国内镜像

您可以：
1. 使用默认的 `docker-compose.yml`（依赖 Docker 镜像加速器配置）
2. 或者修改 `docker-compose.yml` 中特定服务的镜像地址

## 如何选择？

### 推荐使用方式一（官方镜像）如果：
- ✅ 网络可以正常访问 Docker Hub
- ✅ 已配置 Docker 镜像加速器（参考 `DOCKER_TROUBLESHOOTING.md`）
- ✅ 希望使用官方最新镜像

### 推荐使用方式二（国内镜像）如果：
- ✅ 在中国大陆且无法访问 Docker Hub
- ✅ 未配置 Docker 镜像加速器
- ✅ 希望获得更快的下载速度

## 配置 Docker 镜像加速器（推荐）

如果您的网络环境不稳定，建议配置 Docker 镜像加速器，这样可以使用默认的 `docker-compose.yml` 而无需切换到国内镜像配置。

### Windows Docker Desktop

1. 打开 Docker Desktop
2. 设置 → Docker Engine
3. 添加以下配置：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
```

4. 点击 Apply & Restart

配置完成后，即可使用默认的 `docker-compose.yml`。

## 自定义构建

### 只构建应用镜像（使用官方 Dockerfile）

```bash
docker build -t chat-app:latest .
```

### 只构建应用镜像（使用国内镜像 Dockerfile）

```bash
docker build -f Dockerfile.cn -t chat-app:latest .
```

### 使用不同的 Dockerfile 但保持 docker-compose.yml

```bash
# 使用 Dockerfile.cn 构建，但使用默认的 docker-compose.yml
docker-compose build --build-arg DOCKERFILE=Dockerfile.cn
```

不过更简单的方式是直接使用 `docker-compose.cn.yml`。

## 验证镜像

构建完成后，可以查看镜像：

```bash
# 查看所有镜像
docker images

# 查看应用镜像
docker images | grep chat
```

## 常见问题

### Q: 两个 docker-compose 文件会产生冲突吗？

A: 不会。它们是独立的配置文件，使用不同的文件名。只需要在命令中指定 `-f` 参数选择使用哪个文件。

### Q: 可以混用两个配置吗？

A: 不建议。两个配置使用的是相同的容器名称和卷名称，同时运行会产生冲突。请只使用其中一个。

### Q: 切换配置后需要删除旧容器吗？

A: 如果容器名称相同，建议先停止并删除旧容器：

```bash
docker-compose down  # 或 docker-compose -f docker-compose.cn.yml down
```

### Q: 如何知道当前使用的是哪个配置？

A: 查看容器名称：
- `docker-compose.yml` 创建的容器：`chat_mysql`, `chat_redis`, `chat_app`
- `docker-compose.cn.yml` 创建的容器：相同名称（因为它们使用相同的 container_name）

可以通过查看构建日志来判断使用的镜像源。

## 总结

- **默认方式**：`docker-compose up -d --build`（使用官方镜像，需要配置镜像加速器或可访问 Docker Hub）
- **国内环境**：`docker-compose -f docker-compose.cn.yml up -d --build`（使用国内镜像，无需额外配置）

选择最适合您网络环境的配置即可！

