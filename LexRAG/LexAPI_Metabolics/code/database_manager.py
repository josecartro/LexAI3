"""
Database Manager for LexAPI_Metabolics
Handles DuckDB connections for metabolic analysis
"""

import duckdb
from pathlib import Path
from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import MULTIOMICS_DB, GENOMIC_DB

class DatabaseManager:
    """Manages all database connections for metabolics API"""
    
    def get_duckdb_connection(self, db_path: Path, read_only: bool = True):
        """Get DuckDB connection with error handling"""
        if not db_path.exists():
            raise Exception(f"Database not found: {db_path}")
        return duckdb.connect(str(db_path), read_only=read_only)
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test multi-omics DuckDB
        try:
            conn = self.get_duckdb_connection(MULTIOMICS_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["multi_omics"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["multi_omics"] = {"status": "error", "error": str(e)}
        
        # Test genomic DuckDB
        try:
            conn = self.get_duckdb_connection(GENOMIC_DB)
            table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
            conn.close()
            status["genomic_knowledge"] = {"status": "connected", "tables": table_count}
        except Exception as e:
            status["genomic_knowledge"] = {"status": "error", "error": str(e)}
        
        return status
