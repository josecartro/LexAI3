@echo off
echo ================================================================================
echo RESTARTING ALL CORE APIs (Genomics, Anatomics, Literature, Gateway)
echo ================================================================================

pushd LexRAG

echo Killing old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8009') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_Genomics (Port 8001)...
start "LexAPI_Genomics" cmd /k "cd LexAPI_Genomics && api_startup.bat"

echo Starting LexAPI_Anatomics (Port 8002)...
start "LexAPI_Anatomics" cmd /k "cd LexAPI_Anatomics && api_startup.bat"

echo Starting LexAPI_Literature (Port 8003)...
start "LexAPI_Literature" cmd /k "cd LexAPI_Literature && api_startup.bat"

echo Starting LexAPI_AIGateway (Port 8009)...
start "LexAPI_AIGateway" cmd /k "cd LexAPI_AIGateway && api_startup.bat"

echo.
echo APIs restarted. Please wait 15 seconds before testing.

popd
pause

