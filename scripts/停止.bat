@echo off
chcp 65001 >nul
echo ====================================
echo   聊天室应用 - 停止所有服务
echo ====================================
echo.

REM 切换到项目根目录
cd /d %~dp0..

docker-compose -f docker-compose.full.yml down

echo.
echo 服务已停止
pause

