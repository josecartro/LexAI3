"""
Database Configuration for LexAPI_Literature
Centralized database connection settings
"""

# Qdrant settings
QDRANT_URL = "http://localhost:6333"

# API settings
API_PORT = 8003
API_HOST = "0.0.0.0"

# Other API endpoints for cross-integration
OTHER_APIS = {
    "genomics": "http://localhost:8001",
    "anatomics": "http://localhost:8002",
    "metabolics": "http://localhost:8005",
    "populomics": "http://localhost:8006"
}

# Query timeouts
DEFAULT_TIMEOUT = 30
COMPLEX_QUERY_TIMEOUT = 60

def get_database_connections():
    """Get all database connection info"""
    return {
        "qdrant_url": QDRANT_URL,
        "other_apis": OTHER_APIS
    }

