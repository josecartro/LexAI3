"""
Environment Analyzer for LexAPI_Populomics
Handles environmental risk analysis using ClickHouse
"""

from typing import Dict, Any, List
import sys
from pathlib import Path
from datetime import datetime
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

LOCATION_POPULATION_MAP = {
    "spain": "iberian",
    "finland": "finnish",
    "australia": "oceania",
    "sweden": "scandinavian",
    "usa": "american",
    "mexico": "latino"
}

class EnvironmentAnalyzer:
    """Environmental risk analyzer"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
        
    def analyze_environmental_risk(self, location: str, genetic_variants: List[str]) -> Dict[str, Any]:
        population_hint = LOCATION_POPULATION_MAP.get(location.lower(), location)
        try:
            env = self.db_manager.query_environmental_factors(population_hint)
            status = "healthy" if env.get("total_models", 0) > 0 else "insufficient_data"
        except Exception as e:
            env = {"error": str(e)}
            status = "error"
        
        return {
            "location": location,
            "population_hint": population_hint,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "environmental_factors": env,
            "risk_assessment": {
                "recommendations": self._generate_recommendations(population_hint, genetic_variants),
                "genetic_variants_supplied": len(genetic_variants or [])
            }
        }
    
    def _generate_recommendations(self, population_hint: str, genetic_variants: List[str]) -> List[str]:
        recs = [
            f"Leverage population cohort '{population_hint}' for reference baselines.",
            "Integrate air quality and exposure datasets for this region.",
        ]
        if genetic_variants:
            recs.append("Cross-validate supplied variants against local population frequencies.")
        return recs
