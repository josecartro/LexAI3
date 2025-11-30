"""
Database Configuration for LexAPI_Metabolics
Centralized database connection settings
"""

from pathlib import Path

# Database paths
MULTIOMICS_DB = Path("../data/databases/genomic_knowledge/multi_omics.duckdb")
GENOMIC_DB = Path("../data/databases/genomic_knowledge/genomic_knowledge.duckdb")

# API settings
API_PORT = 8005
API_HOST = "0.0.0.0"

# Query timeouts
DEFAULT_TIMEOUT = 30
COMPLEX_QUERY_TIMEOUT = 60

def get_database_paths():
    """Get all database paths for verification"""
    return {
        "multi_omics": MULTIOMICS_DB,
        "genomic_knowledge": GENOMIC_DB
    }
