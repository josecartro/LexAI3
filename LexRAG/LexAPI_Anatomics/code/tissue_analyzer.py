"""
Tissue Analyzer for LexAPI_Anatomics
Handles comprehensive tissue analysis logic using ClickHouse and Neo4j
"""

from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class TissueAnalyzer:
    """Comprehensive tissue analysis"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_tissue_comprehensive(self, tissue_type: str) -> Dict[str, Any]:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing tissue {tissue_type}...")
        
        analysis = {
            "tissue_type": tissue_type,
            "timestamp": datetime.now().isoformat(),
            "expression_data": [],
            "structure": {}
        }
        
        # 1. ClickHouse Expression
        analysis["expression_data"] = self.db_manager.query_gtex_tissue_expression(tissue_type)
        
        # 2. Neo4j Structure
        try:
            with self.db_manager.get_neo4j_session() as session:
                res = session.run("""
                    MATCH (t:Tissue {name: $name})
                    OPTIONAL MATCH (t)-[:PART_OF]->(o:Organ)
                    RETURN t.description, o.name
                """, name=tissue_type).single()
                if res:
                    analysis["structure"] = {"description": res[0], "part_of_organ": res[1]}
        except Exception as e:
            print(f"Neo4j tissue query failed: {e}")
            
        return analysis
