@echo off
echo ============================================================
echo STARTING DNA EXPERT MODEL SERVER (SIMPLE)
echo ============================================================
echo Using basic llama-cpp-python server command
echo ============================================================

echo Checking model file...
if not exist "qwen3-dna-expert.Q4_K_M.gguf" (
    echo [ERROR] Model file not found
    pause
    exit /b 1
)

echo Killing any existing process on port 8010...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8010') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 >nul

echo Starting model server...
echo This will take 30-60 seconds to load...
echo.

python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 0.0.0.0 --port 8010

pause
