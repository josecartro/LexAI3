"""
API Endpoints for LexAPI_Literature
Main controller for literature search and knowledge synthesis
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.database_manager import DatabaseManager
# DatabaseManager now handles Qdrant only
from code.literature_searcher import LiteratureSearcher
from code.knowledge_synthesizer import KnowledgeSynthesizer

# Initialize FastAPI
app = FastAPI(
    title="LexAPI_Literature - Comprehensive Literature Analysis",
    description="Smart literature API with semantic search and knowledge synthesis",
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
# DatabaseManager removed - deprecated (DuckDB)
# Using new managers if needed, but Literature mainly uses Qdrant via Searcher
literature_searcher = LiteratureSearcher()
knowledge_synthesizer = KnowledgeSynthesizer()

@app.get("/health")
async def health_check():
    """Health check with database connectivity verification"""
    try:
        # Instantiate manager just for health check if needed
        db_manager = DatabaseManager()
        databases_status = db_manager.test_all_connections()
        
        return {
            "status": "healthy",
            "service": "LexAPI_Literature",
            "capabilities": [
                "Literature semantic search (Cross-Axis)",
                "Knowledge synthesis",
                "Multi-turn research",
                "Cross-API integration"
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

@app.get("/search/literature/{topic}")
async def search_literature(topic: str, context_apis: Optional[str] = None):
    """Comprehensive literature search with context integration"""
    try:
        context_list = context_apis.split(",") if context_apis else []
        result = literature_searcher.search_literature_comprehensive(topic, context_list)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Literature search failed: {e}")

@app.get("/research/multi_turn/{initial_query}")
async def multi_turn_research(initial_query: str, max_turns: int = 3):
    """Multi-turn research with iterative knowledge building"""
    try:
        result = literature_searcher.research_multi_turn(initial_query, max_turns)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-turn research failed: {e}")

@app.get("/synthesize/knowledge/{domain}")
async def synthesize_knowledge(domain: str):
    """Knowledge synthesis for domain"""
    try:
        result = knowledge_synthesizer.synthesize_domain_knowledge(domain)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge synthesis failed: {e}")
