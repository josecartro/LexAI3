@echo off
echo ============================================================
echo STARTING LEXAPI_METABOLICS
echo ============================================================
echo Purpose: Comprehensive metabolic analysis (Axis 5)
echo Port: 8005
echo Databases: multi_omics.duckdb + genomic_knowledge.duckdb
echo ============================================================

echo Killing any existing process on port 8005...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Metabolics...
python main.py

pause
