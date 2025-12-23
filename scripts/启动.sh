#!/bin/bash

echo "===================================="
echo "  Chat Application - Docker Startup"
echo "===================================="
echo

# Change to project root directory
cd "$(dirname "$0")/.." || exit 1

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running. Please start Docker first."
    exit 1
fi

echo "[1/3] Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose is not installed"
    exit 1
fi

echo "[2/3] Starting all services (MySQL, Redis, Backend, Frontend)..."
echo
echo "Note: First startup may take several minutes to download images..."
echo
docker-compose -f docker-compose.full.yml up -d --build

if [ $? -ne 0 ]; then
    echo
    echo "[ERROR] Service startup failed"
    exit 1
fi

echo
echo "[3/3] Waiting for services to start (frontend build may take longer)..."
sleep 20

echo
echo "Checking service status..."
docker-compose -f docker-compose.full.yml ps

echo
echo "===================================="
echo "  Services started successfully!"
echo "===================================="
echo
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:9000"
echo
echo "View logs: docker-compose -f docker-compose.full.yml logs -f"
echo "Stop services: docker-compose -f docker-compose.full.yml down"
echo
