@echo off
set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
cd /d "%ROOT%"

echo GSPR Project Docker Deployment Script


REM Check if .env exists, if not copy from .env.production
if not exist .env (
    echo [INFO] No .env file found. Creating one from .env.production...
    copy .env.production .env
    echo [IMPORTANT] Please open the .env file and set a secure SECRET_KEY and update CORS_ORIGINS before continuing!
    pause
    exit /b
)

echo [INFO] .env file found. Proceeding with deployment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running or not installed! Please start Docker Desktop or the Docker daemon.
    pause
    exit /b
)

echo [INFO] Shutting down any running containers...
docker compose down
docker rm -f etd-backend etd-frontend >nul 2>&1

echo [INFO] Building and starting containers...
docker compose up -d --build

echo.
echo Deployment started successfully!
echo.
echo Frontend should be available at: http://localhost
echo Backend API should be available at: http://localhost:8000
pause
