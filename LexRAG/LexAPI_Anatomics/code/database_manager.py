"""
Database Manager for LexAPI_Anatomics
Handles Neo4j and DuckDB connections for anatomical analysis
"""

import duckdb
from neo4j import GraphDatabase
from pathlib import Path
from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import DIGITAL_TWIN_DB, NEO4J_URI, NEO4J_AUTH

class DatabaseManager:
    """Manages all database connections for anatomics API"""
    
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    def get_duckdb_connection(self, db_path: Path, read_only: bool = True):
        """Get DuckDB connection with error handling"""
        if not db_path.exists():
            raise Exception(f"Database not found: {db_path}")
        return duckdb.connect(str(db_path), read_only=read_only)
    
    def get_neo4j_session(self):
        """Get Neo4j session"""
        return self.neo4j_driver.session()
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test Neo4j
        try:
            with self.get_neo4j_session() as session:
                anatomy_count = session.run("MATCH (a:Anatomy) RETURN count(a) as count").single()["count"]
                gene_count = session.run("MATCH (g:Gene) RETURN count(g) as count").single()["count"]
                status["neo4j"] = {
                    "status": "connected", 
                    "anatomy_nodes": anatomy_count,
                    "gene_nodes": gene_count
                }
        except Exception as e:
            status["neo4j"] = {"status": "error", "error": str(e)}
        
        # Test Digital Twin DuckDB
        try:
            conn = self.get_duckdb_connection(DIGITAL_TWIN_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["digital_twin"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["digital_twin"] = {"status": "error", "error": str(e)}
        
        return status
    
    def close_connections(self):
        """Close all database connections"""
        try:
            self.neo4j_driver.close()
        except:
            pass