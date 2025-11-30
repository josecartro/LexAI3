@echo off
echo ================================================================================
echo RESTARTING LITERATURE API
echo ================================================================================

pushd LexRAG

echo Killing old process...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_Literature (Port 8003)...
start "LexAPI_Literature" cmd /k "cd LexAPI_Literature && api_startup.bat"

echo.
echo API restarted.

popd
pause

