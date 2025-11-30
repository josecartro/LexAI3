@echo off
echo ================================================================================
echo COMPLETE LEXRAG SYSTEM STARTUP WITH DATABASE CHECKS
echo ================================================================================
echo Checking and starting databases, APIs, and frontend
echo ================================================================================

echo.
echo Step 1: Checking and starting database containers...
echo ================================================================================

echo Checking ClickHouse container status...
docker ps --filter "name=clickhouse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Looking for working ClickHouse container...

echo Checking if clickhouse-fixed is running...
docker ps --filter "name=clickhouse-fixed" --format "{{.Names}}" | findstr clickhouse-fixed >nul
if %errorlevel% == 0 (
    echo SUCCESS: clickhouse-fixed container is running
    set CLICKHOUSE_CONTAINER=clickhouse-fixed
) else (
    echo clickhouse-fixed is not running, starting it...
    docker start clickhouse-fixed
    if %errorlevel% == 0 (
        echo SUCCESS: Started clickhouse-fixed container
        set CLICKHOUSE_CONTAINER=clickhouse-fixed
        echo Waiting 20 seconds for ClickHouse to initialize...
        timeout /t 20 >nul
    ) else (
        echo ERROR: Could not start clickhouse-fixed container
        echo Please check Docker and container status
        pause
        exit /b 1
    )
)

echo.
echo Step 2: Testing database connectivity...
echo ================================================================================

echo Testing ClickHouse HTTP connection...
echo Waiting additional 10 seconds for HTTP interface to be ready...
timeout /t 10 >nul

python LexRAG\test_clickhouse_simple.py

echo.
echo Step 3: Starting LexRAG APIs...
echo ================================================================================

echo Starting LexAPI_Genomics (Port 8001)...
pushd LexRAG\LexAPI_Genomics
start "LexAPI_Genomics" cmd /k "api_startup.bat"
popd

timeout /t 5 >nul

echo Starting LexAPI_Anatomics (Port 8002)...
pushd LexRAG\LexAPI_Anatomics
start "LexAPI_Anatomics" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_Literature (Port 8003)...
pushd LexRAG\LexAPI_Literature
start "LexAPI_Literature" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_Metabolics (Port 8005)...
pushd LexRAG\LexAPI_Metabolics
start "LexAPI_Metabolics" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_Populomics (Port 8006)...
pushd LexRAG\LexAPI_Populomics
start "LexAPI_Populomics" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_Users (Port 8007)...
pushd LexRAG\LexAPI_Users
start "LexAPI_Users" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_DigitalTwin (Port 8008)...
pushd LexRAG\LexAPI_DigitalTwin
start "LexAPI_DigitalTwin" cmd /k "api_startup.bat"
popd

timeout /t 3 >nul

echo Starting LexAPI_AIGateway (Port 8009)...
pushd LexRAG\LexAPI_AIGateway
start "LexAPI_AIGateway" cmd /k "api_startup.bat"
popd

timeout /t 5 >nul

echo.
echo Step 4: Testing API connectivity...
echo ================================================================================

echo Waiting 30 seconds for APIs to start...
timeout /t 30 >nul

echo Testing API health endpoints...
python LexRAG\test_api_health_simple.py

echo.
echo Step 5: Starting frontend...
echo ================================================================================

echo Starting LexUI Frontend (Port 5173)...
if exist ".\lexui\start_frontend.bat" (
    start "LexUI Frontend" cmd /k "cd lexui && start_frontend.bat"
) else (
    echo [WARNING] LexUI frontend startup script not found at ..\lexui\start_frontend.bat
    echo Please check frontend location and try manually
)

timeout /t 5 >nul

echo.
echo ================================================================================
echo COMPLETE LEXRAG PLATFORM STARTUP COMPLETE
echo ================================================================================
echo.
echo System Status:
echo - Database: ClickHouse with 4.4B records
echo - Backend: 8 LexRAG APIs (ports 8001-8009)
echo - Frontend: React interface (port 5173)
echo.
echo Access Points:
echo - Frontend: http://localhost:5173
echo - API Docs: http://127.0.0.1:8007/docs (and other ports)
echo.
echo Manual Setup Required:
echo 1. Open LM Studio
echo 2. Load qwen3-dna-expert.Q4_K_M.gguf model
echo 3. Use simple system prompt (no /think mode)
echo 4. Enable Developer -> Start Server (Port 1234)
echo.
echo AI Integration:
echo - Frontend connects to LM Studio (port 1234) for AI chat
echo - AIGateway (port 8009) provides tool integration with LexRAG APIs
echo - For advanced features, connect AIGateway to LM Studio
echo.
echo Platform will be fully operational once LM Studio is configured
echo ================================================================================

pause
