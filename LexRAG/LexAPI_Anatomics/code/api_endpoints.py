"""
API Endpoints for LexAPI_Anatomics
Main controller for anatomical analysis endpoints
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager
# DatabaseManager removed - deprecated
from code.organ_analyzer import OrganAnalyzer
from code.tissue_analyzer import TissueAnalyzer

# Initialize FastAPI
app = FastAPI(
    title="LexAPI_Anatomics - Comprehensive Anatomical Analysis",
    description="Smart anatomics API for complete anatomical analysis across databases",
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
# DatabaseManager removed - deprecated
organ_analyzer = OrganAnalyzer()
tissue_analyzer = TissueAnalyzer()

@app.get("/health")
async def health_check():
    """Health check with database connectivity verification"""
    try:
        databases_status = db_manager.test_all_connections()
        
        return {
            "status": "healthy",
            "service": "LexAPI_Anatomics",
            "capabilities": [
                "Comprehensive organ analysis (Axis 1)",
                "Gene-anatomy connections",
                "Anatomical structure mapping",
                "Disease-anatomy relationships"
            ],
            "databases": databases_status,
            "architecture": "modular_smart_api",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/analyze/organ/{organ_name}")
async def analyze_organ(organ_name: str):
    """
    Comprehensive organ analysis across all databases
    
    Returns complete anatomical analysis including:
    - Anatomical structure and relationships
    - Gene expression in organ tissues
    - Disease associations
    - Physiological functions
    """
    try:
        result = organ_analyzer.analyze_organ_comprehensive(organ_name)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Organ analysis failed: {e}")

@app.get("/analyze/tissue/{tissue_type}")
async def analyze_tissue(tissue_type: str):
    """
    Comprehensive tissue analysis across all databases
    
    Returns complete tissue profile including:
    - Cellular composition and structure
    - Gene expression patterns
    - Anatomical location and connections
    """
    try:
        result = tissue_analyzer.analyze_tissue_comprehensive(tissue_type)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tissue analysis failed: {e}")

@app.get("/trace/gene_to_anatomy/{gene_symbol}")
async def trace_gene_anatomy(gene_symbol: str):
    """
    Trace gene effects through anatomical systems
    
    Returns comprehensive gene-anatomy mapping including:
    - All anatomical structures where gene is expressed
    - Expression levels and tissue specificity
    - Affected organ systems
    """
    try:
        result = organ_analyzer.trace_gene_to_anatomy(gene_symbol)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gene anatomy tracing failed: {e}")

@app.get("/analyze/disease_anatomy/{disease}")
async def analyze_disease_anatomy(disease: str):
    """
    Analyze anatomical impact of diseases
    
    Returns disease-anatomy connections including:
    - Affected anatomical structures
    - Disease progression pathways
    - Anatomical biomarkers
    """
    try:
        result = organ_analyzer.analyze_disease_anatomy(disease)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease anatomy analysis failed: {e}")

# Add GraphQL endpoint
try:
    from code.simple_graphql import schema
    from strawberry.fastapi import GraphQLRouter
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")
    print("[INFO] GraphQL endpoint added at /graphql")
except ImportError:
    print("[WARNING] GraphQL not available - install strawberry-graphql")
except Exception as e:
    print(f"[WARNING] GraphQL setup failed: {e}")

# Cleanup function
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    db_manager.close_connections()
