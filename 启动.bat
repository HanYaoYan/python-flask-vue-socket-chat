@echo off
chcp 65001 >nul
echo ====================================
echo   聊天室应用 - Docker 一键启动
echo ====================================
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

echo [1/3] 检查 Docker Compose...
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker Compose 未安装
    pause
    exit /b 1
)

echo [2/3] 启动所有服务（MySQL、Redis、后端、前端）...
echo.
echo 提示: 首次启动需要下载镜像，可能需要几分钟时间，请耐心等待...
echo.
docker-compose -f docker-compose.full.yml up -d --build

if errorlevel 1 (
    echo.
    echo [错误] 服务启动失败
    pause
    exit /b 1
)

echo.
echo [3/3] 等待服务启动（前端构建可能需要更长时间）...
timeout /t 20 /nobreak >nul

echo.
echo 检查服务状态...
docker-compose -f docker-compose.full.yml ps

echo.
echo ====================================
echo   服务启动完成！
echo ====================================
echo.
echo 前端访问地址: http://localhost:5173
echo 后端 API 地址: http://localhost:9000
echo.
echo 查看日志: docker-compose -f docker-compose.full.yml logs -f
echo 停止服务: docker-compose -f docker-compose.full.yml down
echo.
pause

