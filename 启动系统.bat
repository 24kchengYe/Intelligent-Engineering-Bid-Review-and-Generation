@echo off
chcp 65001 >nul
echo ========================================
echo Starting Bidding Document Review System
echo ========================================
echo.

cd /d %~dp0

if not exist database mkdir database
if not exist data mkdir data

echo Checking Python environment...
python --version
echo.

echo Starting Streamlit server...
echo The browser will open automatically at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run app.py --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

pause
