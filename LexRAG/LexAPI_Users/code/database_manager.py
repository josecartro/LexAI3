"""
Database Manager for LexAPI_Users
Handles user profile database connections and operations
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
    USER_DB, CLICKHOUSE_HOST, CLICKHOUSE_PORT, 
    CLICKHOUSE_USER, CLICKHOUSE_PASSWORD
)

class UserDatabaseManager:
    """Manages user profile database connections"""
    
    def __init__(self):
        self.clickhouse_client = None
        self.clickhouse_config = {
            "host": CLICKHOUSE_HOST,
            "port": CLICKHOUSE_PORT,
            "username": CLICKHOUSE_USER,
            "password": CLICKHOUSE_PASSWORD
        }
    
    def get_user_db_connection(self, read_only: bool = True):
        """Get user profile database connection"""
        # Create database directory if it doesn't exist
        USER_DB.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(USER_DB), read_only=read_only)
    
    def get_clickhouse_client(self):
        """Get ClickHouse client for reference data (lazy initialization)"""
        if self.clickhouse_client is None:
            self.clickhouse_client = clickhouse_connect.get_client(**self.clickhouse_config)
        return self.clickhouse_client
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test user database
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
        
        # Test ClickHouse connection
        try:
            databases = self.clickhouse_client.query("SHOW DATABASES").result_rows
            total_records = self.clickhouse_client.query("""
                SELECT SUM(total_rows) FROM system.tables 
                WHERE database IN ('genomics_db', 'expression_db', 'proteins_db', 'population_db', 'regulatory_db', 'ontology_db', 'reference_db', 'pathways_db')
            """).result_rows[0][0]
            
            status["clickhouse"] = {
                "status": "connected",
                "databases": len(databases),
                "total_records": f"{total_records:,}",
                "performance": "ultra_fast"
            }
        except Exception as e:
            status["clickhouse"] = {"status": "error", "error": str(e)}
        
        return status
    
    def initialize_user_database(self):
        """Initialize user database with required tables"""
        try:
            conn = self.get_user_db_connection(read_only=False)
            
            # Create user profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    demographics JSON,
                    medical_history JSON,
                    privacy_settings JSON,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user genomics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_genomics (
                    user_id VARCHAR,
                    file_id VARCHAR PRIMARY KEY,
                    file_name VARCHAR,
                    file_type VARCHAR,
                    file_size_mb FLOAT,
                    variant_count INTEGER,
                    processing_status VARCHAR DEFAULT 'uploaded',
                    quality_score FLOAT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_date TIMESTAMP
                )
            """)
            
            # Create user devices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_devices (
                    user_id VARCHAR,
                    device_id VARCHAR PRIMARY KEY,
                    device_type VARCHAR,
                    device_name VARCHAR,
                    last_sync TIMESTAMP,
                    sync_status VARCHAR,
                    data_points_count INTEGER
                )
            """)
            
            # Create user questionnaires table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_questionnaires (
                    user_id VARCHAR,
                    question_id VARCHAR,
                    question_category VARCHAR,
                    question_text VARCHAR,
                    response_value VARCHAR,
                    confidence_score FLOAT,
                    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
    
    def close_connections(self):
        """Close all database connections"""
        try:
            # ClickHouse client doesn't need explicit closing
            pass
        except:
            pass
