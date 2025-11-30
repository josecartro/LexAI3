"""
Database Manager for LexAPI_Populomics
Handles DuckDB connections for population analysis
"""

import duckdb
from pathlib import Path
from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import POPULATION_DB, GENOMIC_DB

class DatabaseManager:
    """Manages all database connections for populomics API"""
    
    def get_duckdb_connection(self, db_path: Path, read_only: bool = True):
        """Get DuckDB connection with error handling"""
        if not db_path.exists():
            raise Exception(f"Database not found: {db_path}")
        return duckdb.connect(str(db_path), read_only=read_only)
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test population risk DuckDB
        try:
            conn = self.get_duckdb_connection(POPULATION_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["population_risk"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["population_risk"] = {"status": "error", "error": str(e)}
        
        # Test genomic DuckDB
        try:
            conn = self.get_duckdb_connection(GENOMIC_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["genomic_knowledge"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["genomic_knowledge"] = {"status": "error", "error": str(e)}
        
        return status
