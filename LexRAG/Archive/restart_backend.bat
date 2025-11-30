@echo off
echo ================================================================================
echo RESTARTING BACKEND APIs ONLY
echo ================================================================================
echo This will update the running code for AIGateway and DigitalTwin
echo ================================================================================

pushd LexRAG

echo Killing old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8008') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8009') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_DigitalTwin (Port 8008)...
start "LexAPI_DigitalTwin" cmd /k "cd LexAPI_DigitalTwin && api_startup.bat"

echo Starting LexAPI_AIGateway (Port 8009)...
start "LexAPI_AIGateway" cmd /k "cd LexAPI_AIGateway && api_startup.bat"

echo Reminder: LM Studio must already be running on port 1234 for chat to work.

echo.
echo APIs restarted. Please wait 10 seconds before testing chat.

popd
pause

