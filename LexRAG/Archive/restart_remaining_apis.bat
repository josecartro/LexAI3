@echo off
echo ================================================================================
echo RESTARTING METABOLICS & POPULOMICS APIs
echo ================================================================================

pushd LexRAG

echo Killing old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_Metabolics (Port 8005)...
start "LexAPI_Metabolics" cmd /k "cd LexAPI_Metabolics && api_startup.bat"

echo Starting LexAPI_Populomics (Port 8006)...
start "LexAPI_Populomics" cmd /k "cd LexAPI_Populomics && api_startup.bat"

echo.
echo APIs restarted. Please wait 10 seconds before testing.

popd
pause
