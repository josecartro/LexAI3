"""
LexAPI_Literature Main Entry Point
Clean, modular literature API with proper imports
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_Literature - Modular Comprehensive Literature Analysis API on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
