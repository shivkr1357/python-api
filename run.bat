@echo off
echo ========================================
echo Python File Management API - Quick Start
echo ========================================
echo.

echo Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
echo.

echo Installing required packages...
pip install -r requirements_simple.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo Starting the server...
echo.
echo The API will be available at:
echo - Main API: http://localhost:8000
echo - Documentation: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python start_server.py

pause
