# Initialize FastAPI
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any

app = FastAPI(
    title="LexAPI_Populomics - Comprehensive Population Analysis",
    description="Smart populomics API for complete population/environmental analysis",
    version="1.0.0",
    docs_url="/docs"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
from code.clickhouse_database_manager import ClickHouseDatabaseManager
db_manager = ClickHouseDatabaseManager()
from code.risk_analyzer import RiskAnalyzer
from code.environment_analyzer import EnvironmentAnalyzer
risk_analyzer = RiskAnalyzer()
environment_analyzer = EnvironmentAnalyzer()

@app.get("/health")
async def health_check():
    """Health check for populomics API."""
    try:
        status = db_manager.test_all_connections()
        return {
            "status": status.get("clickhouse", {}).get("status", "unknown"),
            "service": "LexAPI_Populomics",
            "databases": status,
            "capabilities": [
                "Disease risk aggregation",
                "Population/environmental variant frequencies"
            ]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/analyze/environmental_risk/{location}")
async def analyze_environmental(location: str):
    """Environmental and population exposure analysis."""
    try:
        result = environment_analyzer.analyze_environmental_risk(location, genetic_variants=[])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environmental analysis failed: {e}")

@app.post("/analyze/environmental_risk/{location}")
async def analyze_environmental_with_variants(location: str, variants: List[str]):
    """Same as GET but allows passing user variant list."""
    try:
        result = environment_analyzer.analyze_environmental_risk(location, variants)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environmental analysis failed: {e}")

@app.get("/analyze/disease_risk/{disease_type}")
async def analyze_disease(disease_type: str):
    """Population-wide disease risk summary."""
    try:
        result = risk_analyzer.analyze_disease_risk(disease_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease risk analysis failed: {e}")
