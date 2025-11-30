@echo off
echo ============================================================
echo STARTING LEXAPI_POPULOMICS
echo ============================================================
echo Purpose: Comprehensive population/environmental analysis (Axis 7)
echo Port: 8006
echo Databases: population_risk.duckdb + genomic_knowledge.duckdb
echo ============================================================

echo Killing any existing process on port 8006...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Populomics...
python main.py

pause
