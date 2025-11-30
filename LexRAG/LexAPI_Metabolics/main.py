"""
LexAPI_Metabolics Main Entry Point
Clean, modular metabolics API with proper imports
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_Metabolics - Modular Comprehensive Metabolic Analysis API on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
