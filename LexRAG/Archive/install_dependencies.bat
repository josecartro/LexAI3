@echo off
echo ================================================================================
echo INSTALLING LEXRAG DEPENDENCIES
echo ================================================================================
echo Installing Python packages for AI model integration
echo ================================================================================

echo.
echo Installing llama-cpp-python for AI model server...
pip install llama-cpp-python[server]

echo.
echo Installing additional FastAPI dependencies...
pip install fastapi uvicorn requests python-multipart

echo.
echo Installing database dependencies...
pip install clickhouse-connect duckdb

echo.
echo Installing system monitoring...
pip install psutil

echo.
echo ================================================================================
echo DEPENDENCY INSTALLATION COMPLETE
echo ================================================================================
echo You can now start the AI model server:
echo   cd LexAIModel
echo   start_dna_expert.bat
echo ================================================================================

pause
