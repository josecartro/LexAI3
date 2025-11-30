"""
Database Configuration for LexAPI_Genomics
Centralized database connection settings - ClickHouse Edition
"""

from pathlib import Path

# ClickHouse settings
CLICKHOUSE_HOST = "127.0.0.1"
CLICKHOUSE_PORT = 8125
CLICKHOUSE_USER = "genomics"
CLICKHOUSE_PASSWORD = "genomics123"

# Neo4j settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "000neo4j")

# Legacy DuckDB paths (kept for reference but not active use)
GENOMIC_DB = Path("../data/databases/genomic_knowledge/genomic_knowledge.duckdb")
MULTIOMICS_DB = Path("../data/databases/genomic_knowledge/multi_omics.duckdb")

# API settings
API_PORT = 8001
API_HOST = "0.0.0.0"

# Query timeouts
DEFAULT_TIMEOUT = 30
COMPLEX_QUERY_TIMEOUT = 60

def get_database_config():
    """Get all database connection info"""
    return {
        "clickhouse": {
            "host": CLICKHOUSE_HOST,
            "port": CLICKHOUSE_PORT
        },
        "neo4j_uri": NEO4J_URI
    }
