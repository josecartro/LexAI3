@echo off
echo ================================================================================
echo LEXRAG SYSTEM STARTUP
echo ================================================================================
echo Starting all 8 LexRAG APIs in separate windows
echo Each API queries multiple databases internally for comprehensive analysis
echo ================================================================================

echo.
echo Starting LexAPI_Genomics (Port 8001)...
start "LexAPI_Genomics" cmd /k "cd LexAPI_Genomics && api_startup.bat"

timeout /t 5 >nul

echo Starting LexAPI_Anatomics (Port 8002)...
if exist "LexAPI_Anatomics\api_startup.bat" (
    start "LexAPI_Anatomics" cmd /k "cd LexAPI_Anatomics && api_startup.bat"
) else (
    echo [WARNING] LexAPI_Anatomics startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_Literature (Port 8003)...
if exist "LexAPI_Literature\api_startup.bat" (
    start "LexAPI_Literature" cmd /k "cd LexAPI_Literature && api_startup.bat"
) else (
    echo [WARNING] LexAPI_Literature startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_Metabolics (Port 8005)...
if exist "LexAPI_Metabolics\api_startup.bat" (
    start "LexAPI_Metabolics" cmd /k "cd LexAPI_Metabolics && api_startup.bat"
) else (
    echo [WARNING] LexAPI_Metabolics startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_Populomics (Port 8006)...
if exist "LexAPI_Populomics\api_startup.bat" (
    start "LexAPI_Populomics" cmd /k "cd LexAPI_Populomics && api_startup.bat"
) else (
    echo [WARNING] LexAPI_Populomics startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_Users (Port 8007)...
if exist "LexAPI_Users\api_startup.bat" (
    start "LexAPI_Users" cmd /k "cd LexAPI_Users && api_startup.bat"
) else (
    echo [WARNING] LexAPI_Users startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_DigitalTwin (Port 8008)...
if exist "LexAPI_DigitalTwin\api_startup.bat" (
    start "LexAPI_DigitalTwin" cmd /k "cd LexAPI_DigitalTwin && api_startup.bat"
) else (
    echo [WARNING] LexAPI_DigitalTwin startup script not found
)

timeout /t 3 >nul

echo Starting LexAPI_AIGateway (Port 8009)...
if exist "LexAPI_AIGateway\api_startup.bat" (
    start "LexAPI_AIGateway" cmd /k "cd LexAPI_AIGateway && api_startup.bat"
) else (
    echo [WARNING] LexAPI_AIGateway startup script not found
)

echo.
echo ================================================================================
echo ALL APIS STARTING IN SEPARATE WINDOWS
echo ================================================================================
echo Wait 30 seconds then check:
echo - LexAPI_Genomics: http://localhost:8001/docs
echo - LexAPI_Anatomics: http://localhost:8002/docs  
echo - LexAPI_Literature: http://localhost:8003/docs
echo - LexAPI_Metabolics: http://localhost:8005/docs
echo - LexAPI_Populomics: http://localhost:8006/docs
echo - LexAPI_Users: http://localhost:8007/docs
echo - LexAPI_DigitalTwin: http://localhost:8008/docs
echo - LexAPI_AIGateway: http://localhost:8009/docs
echo - DNA Expert Model: http://localhost:8010/docs
echo ================================================================================
echo.
timeout /t 3 >nul

echo Starting LexUI Frontend (Port 5173)...
start "LexUI Frontend" cmd /k "cd ..\lexui && start_frontend.bat"

echo.
echo ================================================================================
echo COMPLETE LEXRAG PLATFORM STARTING
echo ================================================================================
echo Backend APIs: 8 APIs starting in separate windows
echo Frontend: React interface starting on port 5173
echo.
echo Manual setup required:
echo 1. Open LM Studio
echo 2. Load qwen3-dna-expert.Q4_K_M.gguf model  
echo 3. Enable Developer -> Start Server (Port 1234)
echo.
echo Access points:
echo - Frontend: http://localhost:5173
echo - APIs: http://127.0.0.1:8007/docs (and ports 8001-8009)
echo - LM Studio: http://127.0.0.1:1234 (after manual setup)
echo ================================================================================

pause
