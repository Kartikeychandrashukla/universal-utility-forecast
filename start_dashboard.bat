@echo off
REM Universal Utility Risk Analytics Platform
REM Dashboard Startup Script - Uses Virtual Environment

echo ========================================
echo  Universal Utility Risk Analytics Platform
echo  Starting Dashboard with Virtual Environment...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_venv.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo [INFO] Using virtual environment Python
echo [INFO] All forecasting models (ARIMA, Prophet, Simple MA) are available!
echo.

REM Activate virtual environment and run streamlit
echo [INFO] Starting Streamlit dashboard...
cd /d "%~dp0"
venv\Scripts\python.exe -m streamlit run dashboard/app.py

pause
