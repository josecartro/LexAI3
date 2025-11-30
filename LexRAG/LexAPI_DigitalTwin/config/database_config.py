"""
Database Configuration for LexAPI_DigitalTwin
Digital twin modeling and reference data management
"""

from pathlib import Path

# ClickHouse connection for reference models and fast analysis
CLICKHOUSE_HOST = "127.0.0.1"
CLICKHOUSE_PORT = 8125
CLICKHOUSE_USER = "genomics"
CLICKHOUSE_PASSWORD = "genomics123"

# User database connection (for user data integration)
USER_DB = Path("../data/databases/user_profiles/user_profiles.duckdb")

# Digital twin database (ClickHouse for fast reference data)
DIGITAL_TWIN_DATABASE = "digital_twin_db"

# API settings
API_PORT = 8008
API_HOST = "0.0.0.0"

# Reference model settings
ADAM_MODEL_ID = "adam_default_male"
EVE_MODEL_ID = "eve_default_female"

# Data overlay settings
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,    # User-specific data
    "medium": 0.6,  # Population-matched data
    "low": 0.4      # Reference model data
}

# Query timeouts
DEFAULT_TIMEOUT = 30
COMPLEX_ANALYSIS_TIMEOUT = 120

def get_database_paths():
    """Get all database paths for verification"""
    return {
        "clickhouse_host": CLICKHOUSE_HOST,
        "user_database": USER_DB,
        "digital_twin_db": DIGITAL_TWIN_DATABASE
    }
