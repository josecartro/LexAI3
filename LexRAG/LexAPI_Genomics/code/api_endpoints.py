"""
API Endpoints for LexAPI_Genomics
Main controller file - handles all API endpoints and routes to appropriate analyzers
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
from code.variant_analyzer import VariantAnalyzer
from code.gene_analyzer import GeneAnalyzer
from config.database_config import GENOMIC_DB

# Initialize FastAPI
app = FastAPI(
    title="LexAPI_Genomics - Comprehensive Genetic Analysis",
    description="Smart genomics API querying multiple databases for complete genetic analysis",
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

# Initialize analyzers
db_manager = ClickHouseDatabaseManager()
# duckdb_manager removed - deprecated
variant_analyzer = VariantAnalyzer()
gene_analyzer = GeneAnalyzer()

@app.get("/health")
async def health_check():
    """Health check with database connectivity verification"""
    try:
        databases_status = db_manager.test_all_connections()
        
        return {
            "status": "healthy",
            "service": "LexAPI_Genomics",
            "capabilities": [
                "Comprehensive variant analysis (Axes 2,3,4,6)",
                "Multi-database integration",
                "Causal reasoning support",
                "Batch variant processing"
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

@app.get("/analyze/variant/{variant_id}")
async def analyze_variant(variant_id: str):
    """
    Comprehensive variant analysis across all databases
    
    Returns complete genetic analysis including:
    - Clinical significance from ClinVar
    - Gene expression data from multi-omics
    - Causal connections from Neo4j
    - Clinical assessment and recommendations
    """
    try:
        result = variant_analyzer.analyze_variant_comprehensive(variant_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant analysis failed: {e}")

@app.get("/analyze/gene/{gene_symbol}")
async def analyze_gene(gene_symbol: str):
    """
    Comprehensive gene analysis across all databases
    
    Returns complete gene profile including:
    - All variants and their significance
    - Tissue expression patterns
    - Causal network connections
    - Clinical relevance assessment
    """
    try:
        result = gene_analyzer.analyze_gene_comprehensive(gene_symbol)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gene analysis failed: {e}")

@app.post("/analyze/variant_list")
async def analyze_variant_list(variant_list: List[str]):
    """
    Batch variant analysis for user DNA processing
    
    Processes multiple variants efficiently and returns:
    - Individual variant analyses
    - Batch statistics and success rates
    - Prioritized results based on clinical significance
    """
    try:
        result = variant_analyzer.analyze_variant_batch(variant_list)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch variant analysis failed: {e}")

@app.get("/analyze/gene/{gene_symbol}/proteins")
async def analyze_gene_proteins(gene_symbol: str):
    """
    Gene-to-protein analysis using biomart mapping
    
    Returns complete protein connections including:
    - All proteins produced by the gene
    - Protein IDs and transcript mappings
    - Cross-axis connections (Axis 2 → Axis 4)
    """
    try:
        # Get gene analysis which now includes protein connections
        gene_analysis = gene_analyzer.analyze_gene_comprehensive(gene_symbol)
        
        # Extract and enhance protein information
        protein_connections = gene_analysis.get("protein_connections", {})
        
        if protein_connections and "error" not in protein_connections:
            return {
                "gene_symbol": gene_symbol,
                "protein_analysis": protein_connections,
                "cross_axis_connection": "Axis 2 (Genomics) → Axis 4 (Proteomics)",
                "enhancement": "NEW - biomart_protein_mapping integration",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "gene_symbol": gene_symbol,
                "protein_analysis": {"error": "no_protein_connections_found"},
                "note": "Gene not found in protein mapping database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gene protein analysis failed: {e}")

@app.get("/analyze/gene/{gene_symbol}/pathways")
async def analyze_gene_pathways(gene_symbol: str):
    """
    Gene-to-pathway analysis using KEGG mapping
    
    Returns complete pathway connections including:
    - All metabolic pathways involving the gene
    - Pathway IDs and descriptions
    - Cross-axis connections (Axis 2 → Axis 5)
    """
    try:
        # Get gene analysis which now includes pathway connections
        gene_analysis = gene_analyzer.analyze_gene_comprehensive(gene_symbol)
        
        # Extract and enhance pathway information
        pathway_connections = gene_analysis.get("pathway_connections", {})
        
        if pathway_connections and "error" not in pathway_connections:
            return {
                "gene_symbol": gene_symbol,
                "pathway_analysis": pathway_connections,
                "cross_axis_connection": "Axis 2 (Genomics) → Axis 5 (Metabolomics)",
                "enhancement": "NEW - kegg_gene_pathway_links integration",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "gene_symbol": gene_symbol,
                "pathway_analysis": {"error": "no_pathway_connections_found"},
                "note": "Gene not found in KEGG pathway database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gene pathway analysis failed: {e}")

@app.get("/analyze/variant/{variant_id}/expression")
async def analyze_variant_expression(variant_id: str):
    """
    Variant-to-expression analysis using GTEx eQTL data
    
    Returns tissue-specific expression effects including:
    - Expression changes caused by the variant
    - Affected tissues and effect strengths
    - Cross-axis connections (Axis 2 → Axis 3)
    """
    try:
        # Get variant analysis which now includes expression effects
        variant_analysis = variant_analyzer.analyze_variant_comprehensive(variant_id)
        
        # Extract and enhance expression information
        expression_effects = variant_analysis.get("expression_effects", {})
        
        if expression_effects and "error" not in expression_effects:
            return {
                "variant_id": variant_id,
                "expression_analysis": expression_effects,
                "cross_axis_connection": "Axis 2 (Genomics) → Axis 3 (Transcriptomics)",
                "enhancement": "NEW - gtex_v10_eqtl_associations integration",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "variant_id": variant_id,
                "expression_analysis": {"error": "no_expression_effects_found"},
                "note": "Variant not found in GTEx eQTL database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant expression analysis failed: {e}")

@app.get("/analyze/variant/{variant_id}/splicing")
async def analyze_variant_splicing(variant_id: str):
    """
    Variant-to-splicing analysis using GTEx sQTL data
    
    Returns tissue-specific splicing effects including:
    - Splicing changes caused by the variant
    - Affected tissues and splice events
    - Cross-axis connections (Axis 2 → Axis 3)
    """
    try:
        # Get variant analysis which now includes splicing effects
        variant_analysis = variant_analyzer.analyze_variant_comprehensive(variant_id)
        
        # Extract and enhance splicing information
        splicing_effects = variant_analysis.get("splicing_effects", {})
        
        if splicing_effects and "error" not in splicing_effects:
            return {
                "variant_id": variant_id,
                "splicing_analysis": splicing_effects,
                "cross_axis_connection": "Axis 2 (Genomics) → Axis 3 (Transcriptomics)",
                "enhancement": "NEW - gtex_v10_sqtl_associations integration",
                "analysis_type": "alternative_splicing_effects",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "variant_id": variant_id,
                "splicing_analysis": {"error": "no_splicing_effects_found"},
                "note": "Variant not found in GTEx sQTL database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant splicing analysis failed: {e}")

@app.get("/analyze/variant/{variant_id}/protein_structure")
async def analyze_variant_protein_structure(variant_id: str):
    """
    Variant-to-protein structure analysis using AlphaFold data
    
    Returns protein structure impact including:
    - Protein structure confidence scores
    - Tissue-specific expression patterns
    - Structure quality assessments
    - Cross-axis connections (Axis 2 → Axis 4)
    """
    try:
        # Get variant analysis which now includes protein structure effects
        variant_analysis = variant_analyzer.analyze_variant_comprehensive(variant_id)
        
        # Extract and enhance protein structure information
        structure_effects = variant_analysis.get("protein_structure_effects", {})
        
        if structure_effects and "error" not in structure_effects:
            return {
                "variant_id": variant_id,
                "protein_structure_analysis": structure_effects,
                "cross_axis_connection": "Axis 2 (Genomics) → Axis 4 (Proteomics)",
                "enhancement": "NEW - alphafold_clinical_variant_impact integration",
                "analysis_type": "protein_structure_impact",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "variant_id": variant_id,
                "protein_structure_analysis": {"error": "no_protein_structure_data_found"},
                "note": "Gene not found in AlphaFold database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protein structure analysis failed: {e}")

@app.get("/analyze/variant/{variant_id}/spliceai")
async def analyze_variant_spliceai(variant_id: str):
    """
    Variant SpliceAI analysis using massive production table
    
    Returns splice site predictions including:
    - Acceptor/donor gain/loss scores
    - Splice site impact predictions
    - Access to 3.43 BILLION splice predictions
    """
    try:
        # Get variant analysis which now includes SpliceAI predictions
        variant_analysis = variant_analyzer.analyze_variant_comprehensive(variant_id)
        
        # Extract SpliceAI predictions
        spliceai_predictions = variant_analysis.get("splicing_predictions", {})
        
        if spliceai_predictions and "error" not in spliceai_predictions:
            return {
                "variant_id": variant_id,
                "spliceai_analysis": spliceai_predictions,
                "data_access": "3.43 BILLION splice predictions",
                "enhancement": "NEW - spliceai_scores_production integration",
                "analysis_type": "genome_wide_splice_predictions",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "variant_id": variant_id,
                "spliceai_analysis": {"error": "no_spliceai_predictions_found"},
                "note": "Variant not found in SpliceAI production database",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SpliceAI analysis failed: {e}")

@app.get("/analyze/pathway/{pathway_name}")
async def analyze_pathway(pathway_name: str):
    """
    Comprehensive pathway analysis
    
    Returns complete pathway information including:
    - Member genes and their functions
    - Variants affecting pathway function
    - Tissue-specific pathway activity
    """
    try:
        # This would be implemented with pathway analysis logic
        return {
            "pathway_name": pathway_name,
            "status": "endpoint_implemented",
            "note": "Pathway analysis logic to be implemented",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pathway analysis failed: {e}")


# ============== NEW PROTEIN STRUCTURE ENDPOINTS ==============

@app.get("/analyze/protein/{gene_symbol}")
async def analyze_protein_structure(gene_symbol: str):
    """
    Comprehensive protein structure analysis using AlphaFold + STRING data
    
    Returns:
    - AlphaFold structure confidence (pLDDT scores by region)
    - Protein-protein interactions from STRING (576K interactions)
    - Domain annotations
    - Variant impact on structure
    
    Cross-axis: Axis 2 (Genomics) → Axis 4 (Proteomics)
    """
    try:
        client = db_manager.get_clickhouse_client()
        
        result = {
            "gene_symbol": gene_symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "alphafold_structure": {},
            "protein_interactions": [],
            "domain_info": {},
            "variant_structural_impact": []
        }
        
        # 1. Query AlphaFold structure data
        try:
            alphafold_query = """
                SELECT 
                    uniprot_id,
                    gene_symbol,
                    avg_plddt,
                    high_confidence_pct,
                    low_confidence_pct,
                    sequence_length
                FROM proteins_db.alphafold_structures
                WHERE gene_symbol = %(gene)s
                LIMIT 5
            """
            alphafold_results = client.query(alphafold_query, parameters={"gene": gene_symbol.upper()}).result_rows
            
            if alphafold_results:
                result["alphafold_structure"] = {
                    "uniprot_id": alphafold_results[0][0],
                    "gene_symbol": alphafold_results[0][1],
                    "average_plddt": alphafold_results[0][2],
                    "high_confidence_percent": alphafold_results[0][3],
                    "low_confidence_percent": alphafold_results[0][4],
                    "sequence_length": alphafold_results[0][5],
                    "structure_quality": "high" if alphafold_results[0][2] and alphafold_results[0][2] > 70 else "medium" if alphafold_results[0][2] and alphafold_results[0][2] > 50 else "low"
                }
        except Exception as e:
            result["alphafold_structure"] = {"error": str(e), "note": "AlphaFold query failed"}
        
        # 2. Query STRING protein interactions
        try:
            string_query = """
                SELECT 
                    protein1,
                    protein2,
                    combined_score
                FROM proteins_db.string_interactions
                WHERE protein1 = %(gene)s OR protein2 = %(gene)s
                ORDER BY combined_score DESC
                LIMIT 20
            """
            string_results = client.query(string_query, parameters={"gene": gene_symbol.upper()}).result_rows
            
            if string_results:
                result["protein_interactions"] = [
                    {
                        "partner": row[1] if row[0] == gene_symbol.upper() else row[0],
                        "confidence_score": row[2],
                        "interaction_strength": "strong" if row[2] > 700 else "medium" if row[2] > 400 else "weak"
                    }
                    for row in string_results
                ]
                result["interaction_summary"] = {
                    "total_partners": len(string_results),
                    "strong_interactions": sum(1 for r in string_results if r[2] > 700),
                    "medium_interactions": sum(1 for r in string_results if 400 < r[2] <= 700)
                }
        except Exception as e:
            result["protein_interactions"] = []
            result["string_error"] = str(e)
        
        # 3. Query variants affecting protein structure
        try:
            variant_query = """
                SELECT 
                    rsid,
                    gene_symbol,
                    clinical_significance,
                    consequence_type
                FROM genomics_db.clinvar_variants
                WHERE gene_symbol = %(gene)s
                AND consequence_type LIKE '%missense%'
                LIMIT 20
            """
            variant_results = client.query(variant_query, parameters={"gene": gene_symbol.upper()}).result_rows
            
            if variant_results:
                result["variant_structural_impact"] = [
                    {
                        "rsid": row[0],
                        "significance": row[2],
                        "consequence": row[3],
                        "potential_structure_impact": "high" if "Pathogenic" in str(row[2]) else "uncertain"
                    }
                    for row in variant_results
                ]
        except Exception as e:
            result["variant_structural_impact"] = []
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protein structure analysis failed: {e}")


@app.get("/analyze/protein_interactions/{gene_symbol}")
async def analyze_protein_interactions(gene_symbol: str, min_score: int = 400):
    """
    Protein-protein interaction network analysis using STRING database
    
    Args:
    - gene_symbol: Gene/protein symbol (e.g., "BRCA1", "TP53")
    - min_score: Minimum STRING confidence score (0-1000, default 400)
    
    Returns:
    - Direct interaction partners
    - Interaction scores and confidence
    - Network statistics
    
    Data source: STRING database (576K human protein interactions)
    """
    try:
        client = db_manager.get_clickhouse_client()
        
        query = """
            SELECT 
                protein1,
                protein2,
                combined_score,
                neighborhood_score,
                fusion_score,
                cooccurence_score,
                coexpression_score,
                experimental_score,
                database_score,
                textmining_score
            FROM proteins_db.string_interactions
            WHERE (protein1 = %(gene)s OR protein2 = %(gene)s)
            AND combined_score >= %(min_score)s
            ORDER BY combined_score DESC
            LIMIT 50
        """
        
        results = client.query(query, parameters={
            "gene": gene_symbol.upper(),
            "min_score": min_score
        }).result_rows
        
        interactions = []
        for row in results:
            partner = row[1] if row[0] == gene_symbol.upper() else row[0]
            interactions.append({
                "partner_protein": partner,
                "combined_score": row[2],
                "evidence_scores": {
                    "neighborhood": row[3],
                    "fusion": row[4],
                    "cooccurence": row[5],
                    "coexpression": row[6],
                    "experimental": row[7],
                    "database": row[8],
                    "textmining": row[9]
                },
                "confidence_level": "high" if row[2] > 700 else "medium" if row[2] > 400 else "low"
            })
        
        return {
            "gene_symbol": gene_symbol.upper(),
            "min_score_filter": min_score,
            "total_interactions": len(interactions),
            "interactions": interactions,
            "network_statistics": {
                "high_confidence_partners": sum(1 for i in interactions if i["combined_score"] > 700),
                "medium_confidence_partners": sum(1 for i in interactions if 400 < i["combined_score"] <= 700),
                "avg_interaction_score": sum(i["combined_score"] for i in interactions) / len(interactions) if interactions else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protein interaction analysis failed: {e}")


@app.get("/analyze/splice/{gene_symbol}")
async def analyze_splice_predictions(gene_symbol: str):
    """
    Comprehensive splice prediction analysis for a gene using SpliceAI (3.43B predictions)
    
    Returns:
    - Splice site variants in the gene
    - Acceptor/donor gain/loss predictions
    - Most impactful splice-altering variants
    
    Cross-axis: Axis 2 (Genomics) → Axis 3 (Transcriptomics)
    """
    try:
        client = db_manager.get_clickhouse_client()
        
        # Query SpliceAI predictions for this gene
        query = """
            SELECT 
                chrom,
                pos,
                ref,
                alt,
                gene_symbol,
                ds_ag as acceptor_gain,
                ds_al as acceptor_loss,
                ds_dg as donor_gain,
                ds_dl as donor_loss,
                dp_ag as pos_acceptor_gain,
                dp_al as pos_acceptor_loss,
                dp_dg as pos_donor_gain,
                dp_dl as pos_donor_loss
            FROM genomics_db.spliceai_scores_production
            WHERE gene_symbol = %(gene)s
            AND (ds_ag > 0.2 OR ds_al > 0.2 OR ds_dg > 0.2 OR ds_dl > 0.2)
            ORDER BY greatest(ds_ag, ds_al, ds_dg, ds_dl) DESC
            LIMIT 50
        """
        
        results = client.query(query, parameters={"gene": gene_symbol.upper()}).result_rows
        
        predictions = []
        for row in results:
            max_score = max(row[5] or 0, row[6] or 0, row[7] or 0, row[8] or 0)
            predictions.append({
                "location": f"{row[0]}:{row[1]}",
                "ref": row[2],
                "alt": row[3],
                "gene": row[4],
                "splice_scores": {
                    "acceptor_gain": row[5],
                    "acceptor_loss": row[6],
                    "donor_gain": row[7],
                    "donor_loss": row[8]
                },
                "splice_positions": {
                    "acceptor_gain_pos": row[9],
                    "acceptor_loss_pos": row[10],
                    "donor_gain_pos": row[11],
                    "donor_loss_pos": row[12]
                },
                "max_delta_score": max_score,
                "impact_level": "high" if max_score > 0.5 else "moderate" if max_score > 0.2 else "low"
            })
        
        return {
            "gene_symbol": gene_symbol.upper(),
            "total_splice_variants": len(predictions),
            "predictions": predictions,
            "summary": {
                "high_impact": sum(1 for p in predictions if p["max_delta_score"] > 0.5),
                "moderate_impact": sum(1 for p in predictions if 0.2 < p["max_delta_score"] <= 0.5),
                "data_source": "SpliceAI (3.43 billion predictions)"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Splice prediction analysis failed: {e}")


@app.get("/analyze/regulatory/{variant_id}")
async def analyze_regulatory_variant(variant_id: str):
    """
    Analyze regulatory/non-coding variant using ENCODE data
    
    Returns:
    - Overlapping regulatory elements (enhancers, promoters, etc.)
    - Target genes with confidence
    - Tissue-specific activity
    
    Data source: ENCODE regulatory_db (1.31M elements)
    """
    try:
        client = db_manager.get_clickhouse_client()
        
        result = {
            "variant_id": variant_id,
            "timestamp": datetime.now().isoformat(),
            "regulatory_elements": [],
            "target_genes": [],
            "tissue_activity": {}
        }
        
        # First try to get variant position from clinvar
        variant_query = """
            SELECT chrom, pos, ref, alt, gene_symbol
            FROM genomics_db.clinvar_variants
            WHERE rsid = %(rsid)s
            LIMIT 1
        """
        variant_result = client.query(variant_query, parameters={"rsid": variant_id}).result_rows
        
        if variant_result:
            chrom = variant_result[0][0]
            pos = variant_result[0][1]
            
            # Query overlapping regulatory elements
            reg_query = """
                SELECT 
                    element_id,
                    element_type,
                    chrom,
                    start_pos,
                    end_pos,
                    biosample
                FROM regulatory_db.encode_elements
                WHERE chrom = %(chrom)s
                AND start_pos <= %(pos)s
                AND end_pos >= %(pos)s
                LIMIT 20
            """
            
            reg_results = client.query(reg_query, parameters={
                "chrom": chrom,
                "pos": pos
            }).result_rows
            
            if reg_results:
                result["regulatory_elements"] = [
                    {
                        "element_id": row[0],
                        "type": row[1],
                        "coordinates": f"{row[2]}:{row[3]}-{row[4]}",
                        "biosample": row[5]
                    }
                    for row in reg_results
                ]
            
            # Add the gene from the variant as a target
            if variant_result[0][4]:
                result["target_genes"] = [{"gene": variant_result[0][4], "confidence": "high"}]
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regulatory variant analysis failed: {e}")

@app.get("/query/variants")
async def query_variants(gene: str = None, chromosome: str = None, pathogenic_only: bool = False):
    """
    Flexible variant query endpoint
    
    Allows AI Model to make specific queries like:
    - All variants in a gene
    - All pathogenic variants on a chromosome
    - Custom filtered variant searches
    """
    try:
        # Use ClickHouse client (now that ClickHouse is running)
        client = db_manager.get_clickhouse_client()
        
        # Build dynamic query based on parameters
        where_conditions = []
        
        if gene:
            where_conditions.append(f"gene_symbol = '{gene}'")
        
        if chromosome:
            where_conditions.append(f"chrom = '{chromosome}'")
        
        if pathogenic_only:
            where_conditions.append("clinical_significance LIKE '%Pathogenic%'")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT rsid, gene_symbol, clinical_significance, disease_name
            FROM genomics_db.clinvar_variants
            WHERE {where_clause}
            ORDER BY pos DESC
            LIMIT 100
        """
        
        results = client.query(query).result_rows
        
        return {
            "query_parameters": {
                "gene": gene,
                "chromosome": chromosome,
                "pathogenic_only": pathogenic_only
            },
            "total_results": len(results),
            "variants": [
                {
                    "rsid": row[0],
                    "gene": row[1],
                    "significance": row[2],
                    "disease": row[3]
                }
                for row in results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant query failed: {e}")

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
