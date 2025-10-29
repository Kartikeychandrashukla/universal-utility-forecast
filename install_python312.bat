@echo off
echo ========================================
echo Universal Utility Analytics Platform
echo Python 3.12 Installation Script
echo ========================================
echo.

echo Checking Python version...
python --version
echo.

echo Installing core packages...
echo.

echo [1/8] Installing streamlit...
pip install streamlit>=1.28.0

echo [2/8] Installing pandas...
pip install pandas>=2.1.0

echo [3/8] Installing numpy...
pip install numpy>=1.26.0

echo [4/8] Installing plotly...
pip install plotly>=5.17.0

echo [5/8] Installing scikit-learn...
pip install scikit-learn>=1.3.0

echo [6/8] Installing python-dotenv...
pip install python-dotenv>=1.0.0

echo [7/8] Installing pyyaml...
pip install pyyaml>=6.0.1

echo [8/8] Installing matplotlib (optional)...
pip install matplotlib>=3.8.0

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.

echo Testing installation...
python -c "import streamlit, pandas, numpy, plotly, sklearn; print('✅ All core packages installed successfully!')"

echo.
echo Next steps:
echo 1. Run: streamlit run dashboard/app.py
echo 2. Open: http://localhost:8501
echo.

pause
