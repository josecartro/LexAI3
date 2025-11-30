"""
Gene Analyzer for LexAPI_Genomics
Handles comprehensive gene analysis logic using ClickHouse
"""

from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class GeneAnalyzer:
    """Comprehensive gene analysis across multiple databases (ClickHouse)"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_gene_comprehensive(self, gene_symbol: str) -> Dict[str, Any]:
        """Complete gene analysis across all databases"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing gene {gene_symbol} comprehensively...")
        
        analysis = {
            "gene_symbol": gene_symbol,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": [],
            "variants": {},
            "expression_profile": {},
            "causal_network": {},
            "clinical_relevance": {},
            "comprehensive_summary": ""
        }
        
        # 1. Variant Stats
        try:
            stats = self.db_manager.query_variant_stats_by_gene(gene_symbol)
            if stats:
                analysis["variants"] = stats
                analysis["databases_queried"].append("genomics_db.clinvar_variants")
        except Exception as e:
            print(f"Error querying variant stats: {e}")

        # 2. Expression
        try:
            expr = self.db_manager.query_gene_expression(gene_symbol)
            if expr:
                analysis["expression_profile"] = {"tissues": expr}
                analysis["databases_queried"].append("expression_db.tissue_expression")
        except Exception as e:
            print(f"Error querying expression: {e}")

        # 3. GTEx Summary
        try:
            gtex = self.db_manager.query_gtex_gene_summary(gene_symbol)
            if gtex:
                analysis["gtex_expression_summary"] = gtex
                analysis["databases_queried"].append("expression_db.gtex_eqtl")
        except Exception as e:
            print(f"Error querying GTEx: {e}")

        # 4. SpliceAI
        try:
            splice = self.db_manager.query_splice_predictions(gene_symbol)
            if splice:
                analysis["spliceai_predictions"] = {"predictions": splice[:10]} # Limit
                analysis["databases_queried"].append("genomics_db.spliceai_predictions")
        except Exception as e:
            print(f"Error querying SpliceAI: {e}")

        # 5. Pathways
        try:
            paths = self.db_manager.query_pathways_by_gene(gene_symbol)
            if paths:
                analysis["pathway_connections"] = {"pathways": paths}
                analysis["databases_queried"].append("pathways_db.gene_pathways")
        except Exception as e:
            print(f"Error querying pathways: {e}")

        # 6. Proteins
        try:
            prots = self.db_manager.query_protein_structures(gene_symbol)
            if prots:
                analysis["protein_connections"] = {"structures": prots}
                analysis["databases_queried"].append("proteins_db.alphafold_structures")
        except Exception as e:
            print(f"Error querying proteins: {e}")

        # 7. Neo4j
        try:
            with self.db_manager.get_neo4j_session() as session:
                res = session.run("MATCH (g:Gene {symbol: $sym}) RETURN g.id", sym=gene_symbol).single()
                if res:
                    analysis["causal_network"] = {"neo4j_id": res[0]}
                    analysis["databases_queried"].append("neo4j")
        except Exception as e:
            print(f"Error querying Neo4j: {e}")

        analysis["comprehensive_summary"] = f"Gene {gene_symbol} analysis complete. Queried {len(analysis['databases_queried'])} databases."
        
        return analysis
