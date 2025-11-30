@echo off
echo ================================================================================
echo STARTING NEW LEXRAG APIS IN SEPARATE WINDOWS
echo ================================================================================
echo Starting 3 new APIs + DNA Expert Model Server
echo ================================================================================

echo.
echo DNA Expert Model now runs via LM Studio.
echo Please ensure LM Studio is open, the qwen3-dna-expert model is loaded,
echo and the server is running on Port 1234 before continuing.
echo.
pause

echo Starting LexAPI_Users (Port 8007)...
start "LexAPI_Users" cmd /k "cd LexAPI_Users && api_startup.bat"

timeout /t 3 >nul

echo Starting LexAPI_DigitalTwin (Port 8008)...
start "LexAPI_DigitalTwin" cmd /k "cd LexAPI_DigitalTwin && api_startup.bat"

timeout /t 3 >nul

echo Starting LexAPI_AIGateway (Port 8009)...
start "LexAPI_AIGateway" cmd /k "cd LexAPI_AIGateway && api_startup.bat"

echo.
echo ================================================================================
echo NEW APIS STARTING IN SEPARATE WINDOWS
echo ================================================================================
echo Wait 60 seconds for the APIs to finish booting, then check:
echo - LM Studio server: http://localhost:1234/health (from LM Studio)
echo - LexAPI_Users: http://localhost:8007/docs
echo - LexAPI_DigitalTwin: http://localhost:8008/docs  
echo - LexAPI_AIGateway: http://localhost:8009/docs
echo ================================================================================
echo.
echo NOTE: LM Studio must remain running for the AIGateway to answer questions.
echo ================================================================================
pause
