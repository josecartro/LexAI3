"""
Risk Analyzer for LexAPI_Populomics
Handles disease risk analysis logic using ClickHouse
"""

from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class RiskAnalyzer:
    """Comprehensive risk analyzer"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_disease_risk(self, disease_type: str, user_variants: List[str] = None) -> Dict[str, Any]:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing {disease_type} risk...")
        
        try:
            summary = self.db_manager.query_disease_variants(disease_type, limit=60)
            genetic = {
                "total_variants": summary["total_variants"],
                "disease_variants": summary["disease_variants"],
                "top_genes": summary["top_genes"]
            }
        except Exception as e:
            genetic = {"error": str(e)}
        
        recommendations = self._generate_recommendations(
            disease_type, genetic.get("top_genes", []), user_variants or []
        )
        
        return {
            "disease_type": disease_type,
            "timestamp": datetime.now().isoformat(),
            "genetic_risk_factors": genetic,
            "user_variant_overlaps": self._compare_user_variants(user_variants, genetic),
            "recommendations": recommendations
        }
    
    def _compare_user_variants(self, user_variants: List[str], genetic_summary: Dict[str, Any]) -> Dict[str, Any]:
        if not user_variants or "disease_variants" not in genetic_summary:
            return {"matches": []}
        disease_variants = {variant["variant"] for variant in genetic_summary["disease_variants"]}
        matches = [variant for variant in user_variants if variant in disease_variants]
        return {
            "matches": matches,
            "match_count": len(matches)
        }
    
    def _generate_recommendations(self, disease: str, top_genes: List[Dict[str, Any]], user_variants: List[str]) -> List[str]:
        recs = []
        if not top_genes:
            recs.append(f"Collect more variant data for {disease} to refine the model.")
        else:
            recs.append("Prioritize genes: " + ", ".join(g["gene"] for g in top_genes[:3]))
        if user_variants:
            recs.append("User-provided variants detected; consider personalized counseling.")
        recs.append("Cross-reference environmental exposure with population cohorts.")
        return recs
