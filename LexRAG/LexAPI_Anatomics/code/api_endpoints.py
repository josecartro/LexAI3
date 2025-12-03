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
from code.ontology_analyzer import OntologyAnalyzer

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
ontology_analyzer = OntologyAnalyzer()

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


# ============== NEW ONTOLOGY ENDPOINTS ==============

@app.get("/normalize/phenotype/{phenotype_text}")
async def normalize_phenotype(phenotype_text: str):
    """
    Normalize free-text phenotype description to HPO term(s)
    
    Examples:
    - "kidney cysts" → HP:0000107 (Renal cyst)
    - "seizures" → HP:0001250 (Seizure)
    - "developmental delay" → HP:0001263 (Global developmental delay)
    
    Returns:
    - Normalized HPO term(s) with IDs
    - Confidence scores
    - Neo4j matches if available
    """
    try:
        result = ontology_analyzer.normalize_phenotype(phenotype_text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phenotype normalization failed: {e}")


@app.get("/traverse/uberon/{structure_name}")
async def traverse_uberon_hierarchy(structure_name: str, direction: str = "both", max_depth: int = 3):
    """
    Traverse UBERON anatomical hierarchy
    
    Args:
    - structure_name: Anatomical structure (e.g., "kidney", "heart", "cerebral cortex")
    - direction: "up" (parents), "down" (children), or "both"
    - max_depth: Maximum traversal depth (1-5)
    
    Returns:
    - Parents (is-a, part-of relationships upward)
    - Children (is-a, part-of relationships downward)
    - Siblings (same parent)
    - Related structures
    """
    try:
        if max_depth > 5:
            max_depth = 5
        result = ontology_analyzer.traverse_uberon_hierarchy(structure_name, direction, max_depth)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UBERON traversal failed: {e}")


@app.get("/analyze/phenotype/{phenotype}")
async def analyze_phenotype(phenotype: str):
    """
    Analyze a phenotype - get affected anatomy, related diseases, and genes
    
    Args:
    - phenotype: HPO ID (e.g., "HP:0001250") or symptom name (e.g., "seizures")
    
    Returns:
    - Normalized HPO term
    - Affected anatomical structures
    - Related diseases (MONDO)
    - Associated genes
    """
    try:
        result = {
            "phenotype": phenotype,
            "normalization": ontology_analyzer.normalize_phenotype(phenotype),
            "affected_anatomy": ontology_analyzer.get_anatomy_for_phenotype(phenotype),
            "associated_diseases": ontology_analyzer.map_phenotype_to_diseases([phenotype])
        }
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phenotype analysis failed: {e}")


@app.post("/map/phenotypes_to_diseases")
async def map_phenotypes_to_diseases(phenotypes: List[str]):
    """
    Map multiple phenotypes to candidate diseases (differential diagnosis support)
    
    Args:
    - phenotypes: List of HPO IDs or symptom names
      Example: ["seizures", "hypotonia", "developmental delay"]
    
    Returns:
    - Ranked diseases by phenotype match count
    - Gene associations for top diseases
    - Phenotype coverage analysis
    """
    try:
        result = ontology_analyzer.map_phenotype_to_diseases(phenotypes)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phenotype to disease mapping failed: {e}")


@app.get("/analyze/gene_phenotypes/{gene_symbol}")
async def analyze_gene_phenotypes(gene_symbol: str):
    """
    Get phenotypes and diseases associated with a gene
    
    Args:
    - gene_symbol: Gene symbol (e.g., "BRCA1", "MECP2", "PKD1")
    
    Returns:
    - Associated phenotypes (HPO)
    - Associated diseases (MONDO)
    - Affected anatomical structures
    """
    try:
        with ontology_analyzer.db_manager.get_neo4j_session() as session:
            # Get phenotypes
            phenotypes = session.run("""
                MATCH (g:Gene {symbol: $gene})-[:CAUSES|ASSOCIATED_WITH]-(p)
                WHERE p:Phenotype OR p:HPO
                RETURN DISTINCT p.id as id, p.name as name
                LIMIT 20
            """, gene=gene_symbol.upper()).data()
            
            # Get diseases
            diseases = session.run("""
                MATCH (g:Gene {symbol: $gene})-[:CAUSES|ASSOCIATED_WITH]-(d:Disease)
                RETURN DISTINCT d.id as id, d.name as name
                LIMIT 20
            """, gene=gene_symbol.upper()).data()
            
            # Get anatomy
            anatomy = session.run("""
                MATCH (g:Gene {symbol: $gene})-[:EXPRESSES_IN|AFFECTS]-(a:Anatomy)
                RETURN DISTINCT a.id as id, a.name as name
                LIMIT 20
            """, gene=gene_symbol.upper()).data()
            
            return {
                "gene": gene_symbol.upper(),
                "associated_phenotypes": phenotypes,
                "associated_diseases": diseases,
                "affected_anatomy": anatomy
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gene phenotype analysis failed: {e}")


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
