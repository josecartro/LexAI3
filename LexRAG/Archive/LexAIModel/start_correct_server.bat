@echo off
echo ============================================================
echo STARTING DNA EXPERT MODEL SERVER (CORRECTED)
echo ============================================================
echo Using proper llama-cpp-python server approach
echo Based on: https://llama-cpp-python.readthedocs.io/en/latest/
echo ============================================================

echo Checking model file...
if not exist "qwen3-dna-expert.Q4_K_M.gguf" (
    echo [ERROR] Model file not found: qwen3-dna-expert.Q4_K_M.gguf
    echo Please ensure the model file is in this directory
    pause
    exit /b 1
)

echo Killing any existing process on port 8010...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8010') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting DNA Expert Model Server using documented approach...
echo This may take 30-60 seconds to load the 8.4GB model...
echo.
echo Command: python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 127.0.0.1 --port 8010 --n_ctx 4096 --chat_format chatml
echo.

python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 127.0.0.1 --port 8010 --n_ctx 4096 --chat_format chatml

pause
