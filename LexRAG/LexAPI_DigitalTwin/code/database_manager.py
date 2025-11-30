"""
Database Manager for LexAPI_DigitalTwin
Handles ClickHouse connections and digital twin data operations
"""

import duckdb
import clickhouse_connect
from pathlib import Path
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path for config imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import (
    CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD,
    DIGITAL_TWIN_DATABASE, USER_DB
)

class DigitalTwinDatabaseManager:
    """Manages digital twin database connections and operations"""
    
    def __init__(self):
        self.clickhouse_client = None
        self.clickhouse_config = {
            "host": CLICKHOUSE_HOST,
            "port": CLICKHOUSE_PORT,
            "username": CLICKHOUSE_USER,
            "password": CLICKHOUSE_PASSWORD
        }
    
    def get_clickhouse_client(self):
        """Get ClickHouse client for reference data (lazy initialization)"""
        if self.clickhouse_client is None:
            self.clickhouse_client = clickhouse_connect.get_client(**self.clickhouse_config)
        return self.clickhouse_client
    
    def get_user_db_connection(self, read_only: bool = True):
        """Get user database connection for user data overlay"""
        USER_DB.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(USER_DB), read_only=read_only)
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test ClickHouse connection
        try:
            databases = self.clickhouse_client.query("SHOW DATABASES").result_rows
            
            # Check if digital twin database exists
            twin_db_exists = any(db[0] == DIGITAL_TWIN_DATABASE for db in databases)
            
            # Get reference model count
            if twin_db_exists:
                ref_models = self.clickhouse_client.query(f"SELECT COUNT(*) FROM {DIGITAL_TWIN_DATABASE}.reference_models").result_rows[0][0]
                user_twins = self.clickhouse_client.query(f"SELECT COUNT(*) FROM {DIGITAL_TWIN_DATABASE}.user_twins").result_rows[0][0]
            else:
                ref_models = 0
                user_twins = 0
            
            status["clickhouse"] = {
                "status": "connected",
                "digital_twin_db_exists": twin_db_exists,
                "reference_models": ref_models,
                "user_twins": user_twins,
                "total_databases": len(databases)
            }
        except Exception as e:
            status["clickhouse"] = {"status": "error", "error": str(e)}
        
        # Test user database connection
        try:
            conn = self.get_user_db_connection()
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            conn.close()
            status["user_database"] = {
                "status": "connected",
                "tables": len(tables),
                "location": str(USER_DB)
            }
        except Exception as e:
            status["user_database"] = {"status": "error", "error": str(e)}
        
        return status
    
    def initialize_digital_twin_database(self):
        """Initialize digital twin database with required tables"""
        try:
            # Get ClickHouse client (this will initialize it)
            client = self.get_clickhouse_client()
            
            # Create digital twin database
            client.command(f"CREATE DATABASE IF NOT EXISTS {DIGITAL_TWIN_DATABASE}")
            
            # Create reference models table
            client.command(f"""
                CREATE TABLE IF NOT EXISTS {DIGITAL_TWIN_DATABASE}.reference_models (
                    model_id String,
                    model_name String,
                    sex String,
                    age_category String,
                    demographics JSON,
                    physiology JSON,
                    genomic_baseline JSON,
                    expression_baseline JSON,
                    lifestyle_defaults JSON,
                    health_baseline JSON,
                    created_date DateTime DEFAULT now()
                ) ENGINE = MergeTree()
                ORDER BY (model_name, age_category)
            """)
            
            # Create user digital twins table
            client.command(f"""
                CREATE TABLE IF NOT EXISTS {DIGITAL_TWIN_DATABASE}.user_twins (
                    user_id String,
                    twin_data JSON,
                    data_sources JSON,
                    confidence_scores JSON,
                    completeness_score Float32,
                    last_updated DateTime DEFAULT now()
                ) ENGINE = MergeTree()
                ORDER BY user_id
            """)
            
            # Create population models table
            client.command(f"""
                CREATE TABLE IF NOT EXISTS {DIGITAL_TWIN_DATABASE}.population_models (
                    population_id String,
                    ancestry String,
                    sex String,
                    age_range String,
                    population_data JSON,
                    variant_frequencies JSON,
                    created_date DateTime DEFAULT now()
                ) ENGINE = MergeTree()
                ORDER BY (ancestry, sex, age_range)
            """)
            
            return True
            
        except Exception as e:
            print(f"Digital twin database initialization error: {e}")
            return False
    
    def close_connections(self):
        """Close all database connections"""
        try:
            # ClickHouse client doesn't need explicit closing
            pass
        except:
            pass
