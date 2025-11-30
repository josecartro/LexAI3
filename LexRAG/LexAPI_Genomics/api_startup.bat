@echo off
echo ============================================================
echo STARTING LEXAPI_GENOMICS
echo ============================================================
echo Purpose: Comprehensive genetic analysis (Axes 2,3,4,6)
echo Port: 8001
echo Databases: ClickHouse (4.4B records) + Neo4j + 7-Axis Integration
echo ============================================================

echo Killing any existing process on port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Genomics...
python main.py

pause
