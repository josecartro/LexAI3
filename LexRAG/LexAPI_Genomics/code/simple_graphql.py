"""
Simple GraphQL Implementation for LexAPI_Genomics
Working GraphQL queries without complex imports
"""

import strawberry
from typing import List, Optional
import duckdb
from pathlib import Path

# Simple database connection function
def get_genomic_data(query, params=None):
    """Get data from genomic database"""
    db_path = Path("../data/databases/genomic_knowledge/genomic_knowledge.duckdb")
    conn = duckdb.connect(str(db_path), read_only=True)
    if params:
        result = conn.execute(query, params).fetchall()
    else:
        result = conn.execute(query).fetchall()
    conn.close()
    return result

@strawberry.type
class Variant:
    rsid: str
    gene_symbol: Optional[str] = None
    clinical_significance: Optional[str] = None
    disease_name: Optional[str] = None

@strawberry.type
class Gene:
    symbol: str
    total_variants: Optional[int] = None
    pathogenic_variants: Optional[int] = None

@strawberry.type
class Query:
    
    @strawberry.field
    def variant(self, rsid: str) -> Optional[Variant]:
        """Get variant by rsid"""
        try:
            results = get_genomic_data("""
                SELECT rsid, gene_symbol, clinical_significance, disease_name
                FROM clinvar_full_production
                WHERE rsid = ? OR rsid = ?
                LIMIT 1
            """, [rsid, rsid.replace('rs', '')])
            
            if results:
                row = results[0]
                return Variant(
                    rsid=row[0],
                    gene_symbol=row[1],
                    clinical_significance=row[2],
                    disease_name=row[3]
                )
            return None
            
        except Exception as e:
            print(f"GraphQL variant error: {e}")
            return None
    
    @strawberry.field
    def gene(self, symbol: str) -> Optional[Gene]:
        """Get gene by symbol"""
        try:
            results = get_genomic_data("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN clinical_significance LIKE '%Pathogenic%' THEN 1 END) as pathogenic
                FROM clinvar_full_production
                WHERE gene_symbol = ?
            """, [symbol])
            
            if results and results[0][0] > 0:
                row = results[0]
                return Gene(
                    symbol=symbol,
                    total_variants=row[0],
                    pathogenic_variants=row[1]
                )
            return None
            
        except Exception as e:
            print(f"GraphQL gene error: {e}")
            return None
    
    @strawberry.field
    def search_variants(
        self, 
        gene: Optional[str] = None,
        pathogenic_only: Optional[bool] = False,
        limit: Optional[int] = 10
    ) -> List[Variant]:
        """Search variants with flexible criteria"""
        try:
            where_conditions = []
            params = []
            
            if gene:
                where_conditions.append("gene_symbol = ?")
                params.append(gene)
            
            if pathogenic_only:
                where_conditions.append("clinical_significance LIKE '%Pathogenic%'")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT rsid, gene_symbol, clinical_significance, disease_name
                FROM clinvar_full_production
                WHERE {where_clause}
                ORDER BY pathogenicity_score DESC NULLS LAST
                LIMIT {limit or 10}
            """
            
            results = get_genomic_data(query, params)
            
            return [
                Variant(
                    rsid=row[0],
                    gene_symbol=row[1],
                    clinical_significance=row[2],
                    disease_name=row[3]
                )
                for row in results
            ]
            
        except Exception as e:
            print(f"GraphQL search error: {e}")
            return []

# Create schema
schema = strawberry.Schema(query=Query)

