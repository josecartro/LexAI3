"""
Drug Analyzer for LexAPI_Metabolics
Handles pharmacogenomic analysis using ClickHouse
"""

from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

DRUG_GENE_MAP = {
    "warfarin": ["CYP2C9", "VKORC1", "CYP4F2"],
    "aspirin": ["PTGS1", "PTGS2", "CYP2C19"],
    "ibuprofen": ["CYP2C9", "CYP2C8", "CYP3A4"],
}

class DrugAnalyzer:
    """Drug metabolism analyzer"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
        
    def analyze_drug_metabolism(self, drug_name: str) -> Dict[str, Any]:
        print(f"Analyzing drug: {drug_name}")
        gene_panel = DRUG_GENE_MAP.get(drug_name.lower(), ["CYP2D6", "CYP2C19", "CYP3A4"])
        variants = self._fetch_variants_for_genes(gene_panel)
        generic = self.db_manager.query_drug_metabolism(drug_name)
        
        return {
            "drug_name": drug_name,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": ["genomics_db.clinvar_variants"],
            "pharmacogenomic_factors": {
                "total_pharmacogenomic_variants": len(variants),
                "cyp450_variants": variants,
                "additional_hits": generic
            },
            "recommendations": self._generate_recommendations(gene_panel, len(variants))
        }
    
    def list_pharmacogenomic_variants(self, gene_filter: str = "CYP") -> List[Dict[str, Any]]:
        """Expose variant summary for GraphQL"""
        return self.db_manager.query_cyp_variant_summary(gene_prefix=gene_filter.upper(), limit=40)
    
    def _fetch_variants_for_genes(self, genes: List[str]) -> List[Dict[str, Any]]:
        client = self.db_manager.get_clickhouse_client()
        safe_genes = [g.replace("'", "''") for g in genes]
        gene_list = ", ".join(f"'{g}'" for g in safe_genes)
        query = f"""
        SELECT gene_symbol, rsid, clinical_significance
        FROM genomics_db.clinvar_variants
        WHERE gene_symbol IN ({gene_list})
        ORDER BY gene_symbol, rsid
        LIMIT 60
        """
        rows = client.query(query).result_rows
        return [
            {"gene": row[0], "variant": row[1], "significance": row[2]}
            for row in rows
        ]
    
    def _generate_recommendations(self, genes: List[str], variant_count: int) -> List[str]:
        recs = []
        if variant_count == 0:
            recs.append("No pharmacogenomic variants detected; consider targeted sequencing.")
        else:
            recs.append("Review pharmacogenomic guidelines for detected variants before prescribing.")
        if any(g.startswith("CYP2C") for g in genes):
            recs.append("Monitor dosing adjustments for CYP2C-family metabolizers.")
        if "VKORC1" in genes:
            recs.append("Evaluate VKORC1-related sensitivity for anticoagulants.")
        return recs
