@echo off
echo ================================================================================
echo RESTARTING UPDATED APIs (Genomics & Anatomics)
echo ================================================================================
echo This will apply the ClickHouse database migration
echo ================================================================================

pushd LexRAG

echo Killing old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo Starting LexAPI_Genomics (Port 8001)...
start "LexAPI_Genomics" cmd /k "cd LexAPI_Genomics && api_startup.bat"

echo Starting LexAPI_Anatomics (Port 8002)...
start "LexAPI_Anatomics" cmd /k "cd LexAPI_Anatomics && api_startup.bat"

echo.
echo APIs restarted. Please wait 10 seconds before testing.

popd
pause

