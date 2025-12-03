@echo off
echo ============================================================
echo TESTING DNA EXPERT MODEL (SIMPLE)
echo ============================================================
echo Trying without chat format to test basic generation
echo ============================================================

echo Killing any existing process on port 8010...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8010') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo Starting model without chat format restrictions...
echo This should test basic generation capability...

python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 0.0.0.0 --port 8010 --n_ctx 2048

pause



