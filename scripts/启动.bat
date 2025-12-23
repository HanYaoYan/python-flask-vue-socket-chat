@echo off
echo ====================================
echo   Chat Application - Docker Startup
echo ====================================
echo.

REM Change to project root directory
cd /d %~dp0..
if errorlevel 1 (
    echo [ERROR] Cannot change to project root directory
    pause
    exit /b 1
)

REM Check if Docker is running
echo [1/3] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check Docker Compose
echo [2/3] Checking Docker Compose...
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    pause
    exit /b 1
)

REM Start services
echo [3/3] Starting all services (MySQL, Redis, Backend, Frontend)...
echo.
echo Note: First startup may take several minutes to download images...
echo.
docker-compose -f docker-compose.full.yml up -d --build

if errorlevel 1 (
    echo.
    echo [ERROR] Service startup failed
    pause
    exit /b 1
)

echo.
echo Waiting for services to start (frontend build may take longer)...
timeout /t 20 /nobreak >nul

echo.
echo Checking service status...
docker-compose -f docker-compose.full.yml ps

echo.
echo ====================================
echo   Services started successfully!
echo ====================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:9000
echo.
echo View logs: docker-compose -f docker-compose.full.yml logs -f
echo Stop services: docker-compose -f docker-compose.full.yml down
echo.
pause
