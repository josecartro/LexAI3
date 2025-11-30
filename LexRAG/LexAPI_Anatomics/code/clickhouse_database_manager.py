"""
Database Manager for LexAPI_Anatomics - ClickHouse Edition
Handles ClickHouse and Neo4j connections for anatomical analysis
"""

import clickhouse_connect
from neo4j import GraphDatabase
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for config imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import NEO4J_URI, NEO4J_AUTH

class ClickHouseDatabaseManager:
    """Manages ClickHouse and Neo4j connections for anatomics API"""
    
    def __init__(self):
        self.clickhouse_client = None
        self.clickhouse_config = {
            'host': '127.0.0.1',
            'port': 8125,
            'username': 'genomics',
            'password': 'genomics123'
        }
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    def get_clickhouse_client(self):
        """Get ClickHouse client (lazy initialization)"""
        if self.clickhouse_client is None:
            self.clickhouse_client = clickhouse_connect.get_client(**self.clickhouse_config)
        return self.clickhouse_client
    
    def get_neo4j_session(self):
        """Get Neo4j session"""
        return self.neo4j_driver.session()
    
    def query_gtex_tissue_expression(self, organ_name: str) -> List[Dict]:
        """Query GTEx expression summary for tissues related to organ"""
        # Mapping organ name to tissue regex or match
        query = f"""
        SELECT tissue, count(DISTINCT gene_symbol), avg(mean_tpm)
        FROM expression_db.tissue_expression
        WHERE tissue ILIKE '%{organ_name}%'
        GROUP BY tissue
        ORDER BY avg(mean_tpm) DESC
        LIMIT 20
        """
        try:
            client = self.get_clickhouse_client()
            results = client.query(query).result_rows
            return [
                {
                    "tissue_type": row[0],
                    "genes_expressed": row[1],
                    "avg_expression_level": row[2]
                }
                for row in results
            ]
        except Exception as e:
            print(f"ClickHouse GTEx query failed: {e}")
            return []

    def query_organ_specifications(self, organ_name: str) -> List[Dict]:
        """Query organ specifications from reference DB"""
        # Assuming a table exists, or we mock/fallback. 
        # Let's assume 'reference_db.organ_specs' exists based on Digital Twin context
        query = f"""
        SELECT organ_name, volume_ml, mass_g
        FROM reference_db.organ_specs
        WHERE organ_name ILIKE '%{organ_name}%'
        LIMIT 5
        """
        try:
            client = self.get_clickhouse_client()
            results = client.query(query).result_rows
            return [
                {"organ_name": row[0], "volume_ml": row[1], "mass_g": row[2]}
                for row in results
            ]
        except Exception as e:
            print(f"ClickHouse Organ Specs query failed: {e}")
            return []

    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test ClickHouse
        try:
            self.get_clickhouse_client().query("SELECT 1")
            status["clickhouse"] = {"status": "connected", "performance": "fast"}
        except Exception as e:
            status["clickhouse"] = {"status": "error", "error": str(e)}
        
        # Test Neo4j
        try:
            with self.get_neo4j_session() as session:
                session.run("RETURN 1")
                status["neo4j"] = {"status": "connected"}
        except Exception as e:
            status["neo4j"] = {"status": "error", "error": str(e)}
        
        return status
    
    def close_connections(self):
        try:
            self.neo4j_driver.close()
        except:
            pass

