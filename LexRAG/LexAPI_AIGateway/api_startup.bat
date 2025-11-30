@echo off
echo ============================================================
echo STARTING LEXAPI_AIGATEWAY
echo ============================================================
echo Purpose: AI model integration and query orchestration
echo Port: 8009
echo Dependencies: LM Studio (Port 1234) + All LexRAG APIs
echo ============================================================

echo Killing any existing process on port 8009...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8009') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_AIGateway...
python main.py

pause
