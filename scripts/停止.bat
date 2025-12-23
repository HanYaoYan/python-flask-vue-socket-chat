@echo off
echo ====================================
echo   Chat Application - Stop Services
echo ====================================
echo.

REM Change to project root directory
cd /d %~dp0..

docker-compose -f docker-compose.full.yml down

echo.
echo Services stopped
pause
