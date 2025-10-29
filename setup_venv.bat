@echo off
REM Universal Utility Risk Analytics Platform
REM Virtual Environment Setup Script

echo ========================================
echo  Universal Utility Risk Analytics Platform
echo  Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    echo Please install Python 3.12 and add it to PATH.
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Check if venv already exists
if exist "venv\" (
    echo [WARNING] Virtual environment already exists at 'venv\'
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i not "%RECREATE%"=="y" (
        echo [INFO] Keeping existing virtual environment.
        goto :install_packages
    )
    echo [INFO] Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created successfully!
echo.

:install_packages
REM Install packages
echo [INFO] Installing required packages...
echo [INFO] This may take several minutes...
echo.

venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install -r requirements-full.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Package installation failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo [SUCCESS] Virtual environment is ready!
echo [SUCCESS] All forecasting models installed:
echo   - Simple Moving Average (always available)
echo   - ARIMA (statsmodels + pmdarima)
echo   - Prophet (Facebook Prophet)
echo.
echo To start the dashboard, run: start_dashboard.bat
echo.
pause
