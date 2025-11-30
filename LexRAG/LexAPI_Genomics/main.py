"""
LexAPI_Genomics Main Entry Point
Clean, modular genomics API with proper separation of concerns
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_Genomics - Modular Comprehensive Genetic Analysis API on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
