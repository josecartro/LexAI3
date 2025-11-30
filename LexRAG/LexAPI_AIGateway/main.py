"""
LexAPI_AIGateway Main Entry Point
AI model integration and query orchestration following LexRAG modular pattern
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_AIGateway - AI Model Integration & Query Orchestration on port 8009...")
    uvicorn.run(app, host="0.0.0.0", port=8009)
