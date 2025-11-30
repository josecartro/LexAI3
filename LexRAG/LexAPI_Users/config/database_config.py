"""
Database Configuration for LexAPI_Users
User profile and secure data management
"""

from pathlib import Path

# User database (secure PostgreSQL or DuckDB for development)
USER_DB = Path("../data/databases/user_profiles/user_profiles.duckdb")

# ClickHouse connection for reference data
CLICKHOUSE_HOST = "127.0.0.1"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "genomics"
CLICKHOUSE_PASSWORD = "genomics123"

# API settings
API_PORT = 8007
API_HOST = "0.0.0.0"

# Security settings
JWT_SECRET_KEY = "your-secret-key-here"  # Change in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# File upload settings
MAX_DNA_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
ALLOWED_DNA_FORMATS = [".txt", ".csv", ".vcf", ".gz", ".zip"]
UPLOAD_DIRECTORY = Path("../data/user_uploads")

# Query timeouts
DEFAULT_TIMEOUT = 30
DNA_PROCESSING_TIMEOUT = 300

def get_database_paths():
    """Get all database paths for verification"""
    return {
        "user_profiles": USER_DB,
        "clickhouse_host": CLICKHOUSE_HOST,
        "upload_directory": UPLOAD_DIRECTORY
    }
