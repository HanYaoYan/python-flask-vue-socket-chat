# Docker 故障排查指南

## 网络连接问题

### 问题：无法从 Docker Hub 拉取镜像

**错误信息**：
```
failed to fetch oauth token: Post "https://auth.docker.io/token": dial tcp: connectex: connection failed
```

### 解决方案

#### 方案 1：配置 Docker 镜像加速器（推荐，适用于中国大陆）

1. **Windows Docker Desktop**

   - 打开 Docker Desktop
   - 点击右上角设置图标（齿轮）
   - 进入 **Docker Engine** 设置
   - 在 JSON 配置中添加以下内容：

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

   - 点击 **Apply & Restart**

2. **Linux**

   编辑 `/etc/docker/daemon.json`（如果不存在则创建）：

   ```bash
   sudo mkdir -p /etc/docker
   sudo tee /etc/docker/daemon.json <<-'EOF'
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com",
       "https://mirror.baidubce.com"
     ],
     "dns": ["8.8.8.8", "114.114.114.114"]
   }
   EOF
   ```

   重启 Docker 服务：

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart docker
   ```

#### 方案 2：使用代理（如果有）

如果公司网络需要代理：

1. **Windows Docker Desktop**
   - 设置 → Resources → Proxies
   - 配置 HTTP/HTTPS 代理

2. **Linux**
   在 `/etc/systemd/system/docker.service.d/http-proxy.conf` 中配置：

   ```ini
   [Service]
   Environment="HTTP_PROXY=http://proxy.example.com:8080"
   Environment="HTTPS_PROXY=http://proxy.example.com:8080"
   Environment="NO_PROXY=localhost,127.0.0.1"
   ```

#### 方案 3：手动拉取镜像

如果镜像加速器仍然无法使用，可以尝试：

```bash
# 使用国内镜像源手动拉取
docker pull registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0
docker pull registry.cn-hangzhou.aliyuncs.com/library/redis:6.0-alpine
docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.8-slim

# 然后重新标记
docker tag registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0 mysql:8.0
docker tag registry.cn-hangzhou.aliyuncs.com/library/redis:6.0-alpine redis:6.0-alpine
docker tag registry.cn-hangzhou.aliyuncs.com/library/python:3.8-slim python:3.8-slim
```

#### 方案 4：使用国内镜像源修改 docker-compose.yml

如果以上方法都不行，可以直接在 `docker-compose.yml` 中使用国内镜像：

```yaml
services:
  mysql:
    image: registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0
    # ... 其他配置

  redis:
    image: registry.cn-hangzhou.aliyuncs.com/library/redis:6.0-alpine
    # ... 其他配置
```

### 验证配置

配置完成后，验证是否生效：

```bash
# 查看 Docker 信息
docker info | grep -A 10 "Registry Mirrors"

# 测试拉取镜像
docker pull hello-world
```

### 其他常见问题

#### 问题：DNS 解析失败

**解决方案**：在 Docker daemon.json 中添加 DNS：

```json
{
  "dns": ["8.8.8.8", "114.114.114.114", "223.5.5.5"]
}
```

#### 问题：构建超时

**解决方案**：增加超时时间或使用代理

#### 问题：权限不足

**Windows**：确保以管理员身份运行或使用 Docker Desktop
**Linux**：将用户添加到 docker 组：

```bash
sudo usermod -aG docker $USER
# 然后重新登录
```

### 推荐的镜像加速器地址

- 中科大：`https://docker.mirrors.ustc.edu.cn`
- 网易：`https://hub-mirror.c.163.com`
- 百度：`https://mirror.baidubce.com`
- 阿里云（需登录）：`https://your-id.mirror.aliyuncs.com`

### 获取阿里云镜像加速地址

1. 登录阿里云：https://cr.console.aliyun.com/
2. 进入「容器镜像服务」→「镜像加速器」
3. 复制你的专属加速地址

