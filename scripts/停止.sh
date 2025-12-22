#!/bin/bash

echo "===================================="
echo "  聊天室应用 - 停止所有服务"
echo "===================================="
echo

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1

docker-compose -f docker-compose.full.yml down

echo
echo "服务已停止"

