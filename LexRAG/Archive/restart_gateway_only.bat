@echo off
echo ================================================================================
echo RESTARTING AI GATEWAY (Fixing Timeout)
echo ================================================================================

pushd LexRAG

echo Killing old AI Gateway process...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8009') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_AIGateway (Port 8009)...
start "LexAPI_AIGateway" cmd /k "cd LexAPI_AIGateway && api_startup.bat"

echo.
echo AI Gateway restarted.

popd
pause

