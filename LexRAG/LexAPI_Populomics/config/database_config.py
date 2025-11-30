"""
Database Configuration for LexAPI_Populomics
Centralized database connection settings
"""

from pathlib import Path

# Database paths
POPULATION_DB = Path("../data/databases/population_risk/population_risk.duckdb")
GENOMIC_DB = Path("../data/databases/genomic_knowledge/genomic_knowledge.duckdb")

# API settings
API_PORT = 8006
API_HOST = "0.0.0.0"

# Query timeouts
DEFAULT_TIMEOUT = 30
COMPLEX_QUERY_TIMEOUT = 60

def get_database_paths():
    """Get all database paths for verification"""
    return {
        "population_risk": POPULATION_DB,
        "genomic_knowledge": GENOMIC_DB
    }
