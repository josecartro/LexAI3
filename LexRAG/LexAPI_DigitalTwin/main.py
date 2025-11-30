"""
LexAPI_DigitalTwin Main Entry Point
Digital twin modeling and reference data API following LexRAG modular pattern
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from code.api_endpoints import app

if __name__ == "__main__":
    print("[STARTING] LexAPI_DigitalTwin - Digital Twin Modeling & Reference API on port 8008...")
    uvicorn.run(app, host="0.0.0.0", port=8008)
