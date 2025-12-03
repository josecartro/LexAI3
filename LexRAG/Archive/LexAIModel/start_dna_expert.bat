@echo off
echo ============================================================
echo STARTING DNA EXPERT MODEL SERVER
echo ============================================================
echo Purpose: Qwen3-14B DNA-trained model with llama.cpp
echo Port: 8010
echo Model: qwen3-dna-expert.Q4_K_M.gguf (8.4GB)
echo Context: 32k tokens for complex genomic analysis
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

echo Starting DNA Expert Model Server...
echo This may take 30-60 seconds to load the 8.4GB model...
python model_server.py

pause
