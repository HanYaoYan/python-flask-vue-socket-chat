# Dockerfile - 使用官方镜像源
# 适用于：网络可正常访问 Docker Hub 的环境
# 使用方法: docker-compose up -d --build

FROM python:3.8-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

EXPOSE 9000

CMD ["python3", "app.py"]
