@echo off
echo ============================================================
echo STARTING LEXAPI_USERS
echo ============================================================
echo Purpose: User management and profile API (Digital Twin Foundation)
echo Port: 8007
echo Databases: User Profiles DB + ClickHouse Integration
echo ============================================================

echo Killing any existing process on port 8007...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8007') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Users...
python main.py

pause
