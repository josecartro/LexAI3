@echo off
echo ============================================================
echo STARTING LEXAPI_ANATOMICS
echo ============================================================
echo Purpose: Comprehensive anatomical analysis (Axis 1)
echo Port: 8002
echo Databases: Neo4j + digital_twin.duckdb
echo ============================================================

echo Killing any existing process on port 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Anatomics...
python main.py

pause
