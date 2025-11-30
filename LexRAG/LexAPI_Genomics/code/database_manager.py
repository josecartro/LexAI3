"""
Database Manager for LexAPI_Genomics
Handles all database connections and basic operations
"""

import duckdb
from neo4j import GraphDatabase
from pathlib import Path
from typing import Dict, Any, Optional
import sys
from pathlib import Path
# Add parent directory to path for config imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import GENOMIC_DB, MULTIOMICS_DB, NEO4J_URI, NEO4J_AUTH

class DatabaseManager:
    """Manages all database connections for genomics API"""
    
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
        
        # Test genomic DuckDB
        try:
            conn = self.get_duckdb_connection(GENOMIC_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["genomic_knowledge"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["genomic_knowledge"] = {"status": "error", "error": str(e)}
        
        # Test multi-omics DuckDB
        try:
            conn = self.get_duckdb_connection(MULTIOMICS_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["multi_omics"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["multi_omics"] = {"status": "error", "error": str(e)}
        
        # Test Neo4j
        try:
            with self.get_neo4j_session() as session:
                node_count = session.run("MATCH (n) RETURN count(n) as count LIMIT 1000").single()["count"]
                status["neo4j"] = {"status": "connected", "nodes_sampled": node_count}
        except Exception as e:
            status["neo4j"] = {"status": "error", "error": str(e)}
        
        return status
    
    def close_connections(self):
        """Close all database connections"""
        try:
            self.neo4j_driver.close()
        except:
            pass
