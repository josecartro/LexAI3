# Initialize FastAPI
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI(
    title="LexAPI_Metabolics - Comprehensive Metabolic Analysis",
    description="Smart metabolics API for complete metabolic analysis across databases",
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
from code.metabolism_analyzer import MetabolismAnalyzer
from code.drug_analyzer import DrugAnalyzer
metabolism_analyzer = MetabolismAnalyzer()
drug_analyzer = DrugAnalyzer()

@app.get("/health")
async def health_check():
    """Health check with ClickHouse connectivity verification."""
    try:
        status = db_manager.test_all_connections()
        overall = "healthy" if status.get("clickhouse", {}).get("status") == "connected" else "degraded"
        return {
            "status": overall,
            "service": "LexAPI_Metabolics",
            "databases": status,
            "capabilities": [
                "Metabolomic profile summaries",
                "Pathway enrichment statistics",
                "Pharmacogenomic variant aggregation",
                "GraphQL research endpoints"
            ]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/analyze/metabolism/{user_id}")
async def analyze_metabolism(user_id: str):
    """Comprehensive metabolism analysis for a user."""
    try:
        result = metabolism_analyzer.analyze_metabolism_comprehensive(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metabolism analysis failed: {e}")

@app.get("/analyze/drug_metabolism/{drug_name}")
async def analyze_drug_metabolism(drug_name: str):
    """Analyze pharmacogenomic considerations for a drug."""
    try:
        result = drug_analyzer.analyze_drug_metabolism(drug_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drug metabolism analysis failed: {e}")

# GraphQL router
try:
    from strawberry.fastapi import GraphQLRouter
    from code.simple_graphql import schema
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")
except Exception as e:
    print(f"[WARNING] GraphQL not available: {e}")
