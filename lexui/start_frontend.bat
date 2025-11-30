@echo off
echo ============================================================
echo STARTING LEXUI FRONTEND
echo ============================================================
echo Purpose: React TypeScript frontend for LexRAG platform
echo Port: 5173
echo Features: Registration, DNA Upload, AI Chat, Digital Twin Dashboard
echo ============================================================

echo Checking for existing processes on port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 >nul

echo Starting LexUI frontend...
echo Frontend will be available at: http://localhost:5173
echo.
echo Features available:
echo - User registration with ancestry collection
echo - DNA file upload (23andMe, AncestryDNA, etc.)
echo - AI chat with DNA Expert model
echo - Digital twin visualization
echo - 4.4B genomic record access
echo.

npm run dev

pause
