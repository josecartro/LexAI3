"""
Database Manager for LexAPI_Metabolics - ClickHouse Edition
Handles ClickHouse connections for metabolic analysis
"""

import clickhouse_connect
from typing import Dict, Any, List
import sys
from pathlib import Path

class ClickHouseDatabaseManager:
    """Manages ClickHouse connections for metabolics API"""
    
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
    
    def query_drug_metabolism(self, drug_name: str) -> List[Dict]:
        """Query drug metabolism from PharmGKB (in ClickHouse)"""
        try:
            client = self.get_clickhouse_client()
            safe_drug = drug_name.replace("'", "''")
            query = f"""
            SELECT rsid, gene_symbol, clinical_significance
            FROM genomics_db.clinvar_variants
            WHERE clinical_significance ILIKE '%drug%'
               OR disease_name ILIKE '%{safe_drug}%'
               OR gene_symbol LIKE 'CYP%'
            LIMIT 50
            """
            results = client.query(query).result_rows
            return [
                {
                    "variant": row[0],
                    "gene": row[1],
                    "significance": row[2]
                }
                for row in results
            ]
        except Exception as e:
            print(f"Drug query failed: {e}")
            return []
    
    def query_top_pathways(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return pathway usage statistics"""
        client = self.get_clickhouse_client()
        query = f"""
        SELECT pathway_name, count() AS gene_count
        FROM pathways_db.gene_pathways
        GROUP BY pathway_name
        ORDER BY gene_count DESC
        LIMIT {limit}
        """
        rows = client.query(query).result_rows
        return [
            {"pathway_name": row[0], "gene_count": row[1]}
            for row in rows
        ]
    
    def query_pathway_samples(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Return sample pathway metrics for metabolomic profile."""
        client = self.get_clickhouse_client()
        query = f"""
        SELECT pathway_name, any(gene_symbol) AS representative_gene, count() AS gene_count
        FROM pathways_db.gene_pathways
        GROUP BY pathway_name
        ORDER BY gene_count DESC
        LIMIT {limit}
        """
        rows = client.query(query).result_rows
        return [
            {
                "pathway_name": row[0],
                "gene_symbol": row[1],
                "gene_count": row[2]
            }
            for row in rows
        ]
    
    def query_cyp_variant_summary(self, gene_prefix: str = "CYP", limit: int = 25) -> List[Dict[str, Any]]:
        """Return CYP450 variant summary for pharmacogenomics."""
        client = self.get_clickhouse_client()
        safe_prefix = gene_prefix.replace("'", "''")
        query = f"""
        SELECT gene_symbol, rsid, clinical_significance
        FROM genomics_db.clinvar_variants
        WHERE gene_symbol LIKE '{safe_prefix}%'
        ORDER BY gene_symbol, rsid
        LIMIT {limit}
        """
        rows = client.query(query).result_rows
        return [
            {"gene": row[0], "variant": row[1], "significance": row[2]}
            for row in rows
        ]
    
    def search_pathways(self, term: str, limit: int = 10) -> List[str]:
        """Search pathway names by substring."""
        client = self.get_clickhouse_client()
        safe_term = term.replace("'", "''")
        query = f"""
        SELECT DISTINCT pathway_name
        FROM pathways_db.gene_pathways
        WHERE lower(pathway_name) LIKE lower('%{safe_term}%')
        LIMIT {limit}
        """
        rows = client.query(query).result_rows
        return [row[0] for row in rows]

    def close_connections(self):
        pass
