@echo off
REM Test script for RiddleNet Gunicorn setup on Windows
REM This script tests the Gunicorn configuration using Docker

echo Testing RiddleNet Gunicorn Setup
echo ==================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows
    pause
    exit /b 1
)

echo Docker is available

REM Check if required files exist
echo.
echo Checking required files...
if not exist "wsgi.py" (
    echo ERROR: wsgi.py not found
    pause
    exit /b 1
)
echo ✅ wsgi.py exists

if not exist "gunicorn.conf.py" (
    echo ERROR: gunicorn.conf.py not found
    pause
    exit /b 1
)
echo ✅ gunicorn.conf.py exists

if not exist "run.py" (
    echo ERROR: run.py not found
    pause
    exit /b 1
)
echo ✅ run.py exists

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)
echo ✅ requirements.txt exists

echo.
echo Building Docker image for testing...
docker build -t riddlenet-test .
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo.
echo Starting RiddleNet with Gunicorn in Docker...
echo This will test the production configuration locally
echo The application will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the test server
echo.

docker run --rm -p 8000:8000 --name riddlenet-test riddlenet-test

pause