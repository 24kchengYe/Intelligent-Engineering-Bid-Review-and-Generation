@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Starting on Alternative Port 8502
echo ========================================
echo.

if not exist database mkdir database
if not exist data mkdir data

echo Starting with disabled XSRF protection...
echo Access URL: http://localhost:8502
echo ========================================
echo.

streamlit run app.py --server.port 8502 --server.enableCORS false --server.enableXsrfProtection false

pause
