"""
Simple GraphQL Implementation for LexAPI_Metabolics
Working GraphQL queries for metabolic data
"""

import strawberry
from typing import List, Optional
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.metabolism_analyzer import MetabolismAnalyzer
from code.drug_analyzer import DrugAnalyzer
from code.clickhouse_database_manager import ClickHouseDatabaseManager

metabolism_analyzer = MetabolismAnalyzer()
drug_analyzer = DrugAnalyzer()
db_manager = ClickHouseDatabaseManager()

@strawberry.type
class MetaboliteData:
    metabolite_id: str
    concentration: Optional[float] = None
    unit: Optional[str] = None
    sample_type: Optional[str] = None

@strawberry.type
class PathwayActivity:
    pathway_id: str
    activity_score: Optional[float] = None
    confidence: Optional[float] = None

@strawberry.type
class PharmacogenomicVariant:
    gene: str
    variant: str
    significance: str
    metabolic_relevance: Optional[str] = None

@strawberry.type
class Query:
    
    @strawberry.field
    def metabolites_for_user(self, user_id: str) -> List[MetaboliteData]:
        """Get metabolite data for user"""
        analysis = metabolism_analyzer.analyze_metabolism_comprehensive(user_id)
        samples = analysis.get("metabolomic_profile", {}).get("sample_metabolites", [])
        metabolite_list = []
        for item in samples:
            metabolite_list.append(
                MetaboliteData(
                    metabolite_id=item.get("metabolite_id", "unknown"),
                    concentration=item.get("gene_count"),
                    unit="gene_count",
                    sample_type=item.get("pathway")
                )
            )
        return metabolite_list
    
    @strawberry.field
    def pathway_activities(self, user_id: str) -> List[PathwayActivity]:
        """Get pathway activities for user"""
        analysis = metabolism_analyzer.analyze_metabolism_comprehensive(user_id)
        top_pathways = analysis.get("pathway_analysis", {}).get("top_pathways", [])
        return [
            PathwayActivity(
                pathway_id=row.get("pathway_name", "unknown"),
                activity_score=row.get("gene_count"),
                confidence=row.get("gene_count")
            )
            for row in top_pathways
        ]
    
    @strawberry.field
    def pharmacogenomic_variants(self, gene_filter: Optional[str] = None) -> List[PharmacogenomicVariant]:
        """Get pharmacogenomic variants"""
        prefix = gene_filter if gene_filter else "CYP"
        variants = drug_analyzer.list_pharmacogenomic_variants(prefix)
        return [
            PharmacogenomicVariant(
                gene=item.get("gene", "unknown"),
                variant=item.get("variant", "unknown"),
                significance=item.get("significance", "unknown"),
                metabolic_relevance="drug_metabolism" if "CYP" in item.get("gene", "") else "phase2_metabolism"
            )
            for item in variants
        ]
    
    @strawberry.field
    def search_metabolic_pathways(self, pathway_name: str) -> List[str]:
        """Search for metabolic pathways"""
        results = db_manager.search_pathways(pathway_name, limit=10)
        return results

# Create schema
schema = strawberry.Schema(query=Query)

