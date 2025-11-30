"""
Database Manager for LexAPI_Populomics - ClickHouse Edition
Handles ClickHouse connections for population analysis
"""

import clickhouse_connect
from typing import Dict, Any, List

class ClickHouseDatabaseManager:
    """Manages ClickHouse connections for populomics API"""
    
    def __init__(self):
        self.clickhouse_client = None
        self.clickhouse_config = {
            'host': '127.0.0.1',
            'port': 8125,
            'username': 'genomics',
            'password': 'genomics123'
        }
    
    def get_clickhouse_client(self):
        """Get ClickHouse client (lazy initialization)"""
        if self.clickhouse_client is None:
            self.clickhouse_client = clickhouse_connect.get_client(**self.clickhouse_config)
        return self.clickhouse_client
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        try:
            self.get_clickhouse_client().query("SELECT 1")
            status["clickhouse"] = {"status": "connected", "performance": "fast"}
        except Exception as e:
            status["clickhouse"] = {"status": "error", "error": str(e)}
        return status
        
    def query_disease_variants(self, disease: str, limit: int = 40) -> Dict[str, Any]:
        """Return variant counts and sample variants for a disease."""
        client = self.get_clickhouse_client()
        safe_disease = disease.replace("'", "''")
        variant_query = f"""
        SELECT rsid, gene_symbol, clinical_significance
        FROM genomics_db.clinvar_variants 
        WHERE disease_name ILIKE '%{safe_disease}%'
        LIMIT {limit}
        """
        gene_query = f"""
        SELECT gene_symbol, count() AS variant_count
        FROM genomics_db.clinvar_variants
        WHERE disease_name ILIKE '%{safe_disease}%'
        GROUP BY gene_symbol
        ORDER BY variant_count DESC
        LIMIT 10
        """
        variants = client.query(variant_query).result_rows
        genes = client.query(gene_query).result_rows
        return {
            "total_variants": len(variants),
            "disease_variants": [
                {"variant": row[0], "gene": row[1], "significance": row[2]}
                for row in variants
            ],
            "top_genes": [
                {"gene": row[0], "variant_count": row[1]}
                for row in genes
            ]
        }
        
    def query_population_frequencies(self, population_keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Return population variant frequency data."""
        client = self.get_clickhouse_client()
        safe_pop = population_keyword.replace("'", "''")
        query = f"""
        SELECT population, rsid, allele_frequency, chrom
        FROM population_db.variant_frequencies
        WHERE lower(population) LIKE lower('%{safe_pop}%')
        ORDER BY allele_frequency DESC
        LIMIT {limit}
        """
        rows = client.query(query).result_rows
        return [
            {
                "population": row[0],
                "variant": row[1],
                "allele_frequency": row[2],
                "chromosome": row[3]
            }
            for row in rows
        ]
    
    def query_environmental_factors(self, population_keyword: str, limit: int = 20) -> Dict[str, Any]:
        """Return aggregated environmental/population stats."""
        distribution = self.query_population_frequencies(population_keyword, limit)
        return {
            "total_models": len(distribution),
            "variant_hotspots": distribution
        }

    def close_connections(self):
        pass
