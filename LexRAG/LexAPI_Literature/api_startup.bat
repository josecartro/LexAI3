@echo off
echo ============================================================
echo STARTING LEXAPI_LITERATURE
echo ============================================================
echo Purpose: Comprehensive literature/knowledge search (Cross-Axis)
echo Port: 8003
echo Databases: Qdrant + cross-API integration
echo ============================================================

echo Killing any existing process on port 8003...
for /f "tokens=5" %%a in ('netstar -ano ^| findstr :8003') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting LexAPI_Literature...
python main.py

pause
