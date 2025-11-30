"""
LexAPI_Populomics Main Entry Point
Clean, modular populomics API with proper imports
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_Populomics - Modular Comprehensive Population Analysis API on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)
