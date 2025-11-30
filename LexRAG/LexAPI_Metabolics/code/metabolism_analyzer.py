"""
Metabolism Analyzer for LexAPI_Metabolics
Handles comprehensive metabolic analysis logic using ClickHouse
"""

from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class MetabolismAnalyzer:
    """Comprehensive metabolic analyzer"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_metabolism_comprehensive(self, user_id: str) -> Dict[str, Any]:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing metabolism for {user_id}...")
        
        analysis = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": [],
            "metabolomic_profile": {},
            "pathway_analysis": {},
            "genetic_factors": {},
            "comprehensive_summary": ""
        }
        
        try:
            samples = self.db_manager.query_pathway_samples(limit=15)
            analysis["metabolomic_profile"] = {
                "total_metabolites": len(samples),
                "sample_metabolites": [
                    {
                        "metabolite_id": f"{row['pathway_name']}::{row['gene_symbol']}",
                        "pathway": row["pathway_name"],
                        "gene_symbol": row["gene_symbol"],
                        "gene_count": row["gene_count"]
                    }
                    for row in samples
                ]
            }
            analysis["databases_queried"].append("pathways_db.gene_pathways")
        except Exception as e:
            analysis["metabolomic_profile"] = {"error": str(e)}
        
        try:
            top_pathways = self.db_manager.query_top_pathways(limit=8)
            analysis["pathway_analysis"] = {
                "total_pathways": len(top_pathways),
                "top_pathways": top_pathways
            }
            if "pathways_db.gene_pathways" not in analysis["databases_queried"]:
                analysis["databases_queried"].append("pathways_db.gene_pathways")
        except Exception as e:
            analysis["pathway_analysis"] = {"error": str(e)}
        
        try:
            cyp_summary = self.db_manager.query_cyp_variant_summary(limit=30)
            analysis["genetic_factors"] = {
                "total_variants": len(cyp_summary),
                "cyp450_variants": cyp_summary
            }
            analysis["databases_queried"].append("genomics_db.clinvar_variants")
        except Exception as e:
            analysis["genetic_factors"] = {"error": str(e)}
            
        analysis["comprehensive_summary"] = (
            f"Metabolic pathways analyzed for user {user_id}. "
            f"Total metabolites sampled: {analysis.get('metabolomic_profile', {}).get('total_metabolites', 0)}. "
            f"CYP variants discovered: {analysis.get('genetic_factors', {}).get('total_variants', 0)}."
        )
        return analysis

    def analyze_pathway_metabolism(self, pathway: str) -> Dict[str, Any]:
        """Detailed look at a specific pathway."""
        try:
            matching = [
                row for row in self.db_manager.query_pathway_samples(limit=50)
                if pathway.lower() in row["pathway_name"].lower()
            ]
            return {
                "pathway": pathway,
                "matches": matching,
                "total_matches": len(matching)
            }
        except Exception as e:
            return {"pathway": pathway, "error": str(e)}
