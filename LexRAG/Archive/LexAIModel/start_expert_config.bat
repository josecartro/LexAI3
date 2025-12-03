@echo off
echo ============================================================
echo STARTING DNA EXPERT MODEL (EXPERT CONFIGURATION)
echo ============================================================
echo Using expert recommendations for RTX 4090 + 14B model
echo Based on professional llama.cpp guidance
echo ============================================================

echo Checking model file...
if not exist "qwen3-dna-expert.Q4_K_M.gguf" (
    echo [ERROR] Model file not found: qwen3-dna-expert.Q4_K_M.gguf
    pause
    exit /b 1
)

echo Killing any existing processes on port 8010...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8010') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting DNA Expert Model with expert configuration...
echo GPU: RTX 4090 (16GB VRAM)
echo Model: 14B parameters with Q4_K_M quantization
echo Settings: Optimized for GPU offload and performance
echo.

python -m llama_cpp.server ^
  --model qwen3-dna-expert.Q4_K_M.gguf ^
  --host 127.0.0.1 ^
  --port 8010 ^
  --n_gpu_layers 40 ^
  --n_ctx 8192 ^
  --n_batch 64

echo.
echo Model should be available at: http://127.0.0.1:8010
echo GPU acceleration enabled with 40 layers offloaded
echo.

pause
