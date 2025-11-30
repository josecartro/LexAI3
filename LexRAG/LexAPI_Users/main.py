"""
LexAPI_Users Main Entry Point
User management and profile API following LexRAG modular pattern
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_Users - User Management & Profile API on port 8007...")
    uvicorn.run(app, host="0.0.0.0", port=8007)
