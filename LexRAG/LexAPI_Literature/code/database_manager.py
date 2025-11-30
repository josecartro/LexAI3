"""
Database Manager for LexAPI_Literature
Handles Qdrant connections and cross-API integration
"""

from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import QDRANT_URL

class DatabaseManager:
    """Manages Qdrant connection for literature API"""
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test Qdrant connection"""
        status = {}
        
        # Test Qdrant
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=QDRANT_URL)
            # Simple check
            collections = client.get_collections()
            status["qdrant"] = {
                "status": "connected", 
                "collections_count": len(collections.collections)
            }
        except Exception as e:
            status["qdrant"] = {"status": "error", "error": str(e)}
        
        return status
