@echo off
echo ============================================================
echo STARTING LEXAPI_DIGITALTWIN
echo ============================================================
echo Purpose: Digital twin modeling with Adam/Eve reference models
echo Port: 8008
echo Databases: ClickHouse (Reference Models) + User DB Integration
echo ============================================================

echo Killing any existing process on port 8008...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8008') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_DigitalTwin...
python main.py

pause
