"""
Organ Analyzer for LexAPI_Anatomics
Handles comprehensive organ analysis logic using ClickHouse and Neo4j
"""

from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class OrganAnalyzer:
    """Comprehensive organ analysis across multiple databases"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_organ_comprehensive(self, organ_name: str) -> Dict[str, Any]:
        """Complete organ analysis across all databases"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing organ {organ_name} comprehensively...")
        
        analysis = {
            "organ_name": organ_name,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": [],
            "anatomical_structure": {},
            "genetic_connections": {},
            "disease_associations": {},
            "comprehensive_summary": ""
        }
        
        # Query Neo4j for anatomical structure
        analysis["anatomical_structure"] = self._query_anatomical_structure(organ_name)
        if analysis["anatomical_structure"] and "error" not in analysis["anatomical_structure"]:
            analysis["databases_queried"].append("neo4j_anatomy")
        
        # Query genetic connections (Neo4j)
        analysis["genetic_connections"] = self._query_genetic_connections(organ_name)
        if analysis["genetic_connections"] and "error" not in analysis["genetic_connections"]:
            analysis["databases_queried"].append("neo4j_genetics")
        
        # Query disease associations (Neo4j)
        analysis["disease_associations"] = self._query_disease_associations(organ_name)
        if analysis["disease_associations"] and "error" not in analysis["disease_associations"]:
            analysis["databases_queried"].append("neo4j_diseases")
        
        # Query GTEx tissue expression data (ClickHouse)
        analysis["tissue_expression_data"] = self.db_manager.query_gtex_tissue_expression(organ_name)
        if analysis["tissue_expression_data"]:
            analysis["databases_queried"].append("clickhouse_expression_db")
        
        # Query organ specifications (ClickHouse)
        analysis["physiological_data"] = self.db_manager.query_organ_specifications(organ_name)
        if analysis["physiological_data"]:
            analysis["databases_queried"].append("clickhouse_reference_db")
        
        # Generate summary
        analysis["comprehensive_summary"] = self._generate_organ_summary(analysis)
        
        return analysis
    
    def _query_anatomical_structure(self, organ_name: str) -> Dict[str, Any]:
        """Query Neo4j for anatomical structure information"""
        try:
            with self.db_manager.get_neo4j_session() as session:
                anatomy_result = session.run("""
                    MATCH (a:Anatomy) 
                    WHERE toLower(a.name) CONTAINS toLower($organ_name)
                    RETURN a.name, a.id, labels(a) as labels
                    LIMIT 10
                """, organ_name=organ_name).data()
                
                if anatomy_result:
                    return {
                        "matching_structures": [
                            {"name": r["a.name"], "id": r["a.id"], "types": r["labels"]}
                            for r in anatomy_result
                        ],
                        "total_matches": len(anatomy_result)
                    }
                    return {"error": "no_anatomical_matches_found"}
        except Exception as e:
            return {"error": str(e)}
    
    def _query_genetic_connections(self, organ_name: str) -> Dict[str, Any]:
        try:
            with self.db_manager.get_neo4j_session() as session:
                gene_connections = session.run("""
                    MATCH (g:Gene)-[e:EXPRESSES_IN]->(a:Anatomy)
                    WHERE toLower(a.name) CONTAINS toLower($organ_name)
                    RETURN g.symbol as gene, e.expression_level as level
                    LIMIT 20
                """, organ_name=organ_name).data()
                
                if gene_connections:
                    return {"expressed_genes": gene_connections}
                    return {"error": "no_genetic_connections_found"}
        except Exception as e:
            return {"error": str(e)}
    
    def _query_disease_associations(self, organ_name: str) -> Dict[str, Any]:
        try:
            with self.db_manager.get_neo4j_session() as session:
                disease_connections = session.run("""
                    MATCH (d:Disease)
                    WHERE toLower(d.name) CONTAINS toLower($organ_name)
                    RETURN DISTINCT d.name as disease
                    LIMIT 10
                """, organ_name=organ_name).data()
                
                if disease_connections:
                    return {"related_diseases": [d["disease"] for d in disease_connections]}
                    return {"error": "no_disease_associations_found"}
        except Exception as e:
            return {"error": str(e)}
    
    def trace_gene_to_anatomy(self, gene_symbol: str) -> Dict[str, Any]:
        """Trace gene effects through anatomical systems"""
        try:
            with self.db_manager.get_neo4j_session() as session:
                effects = session.run("""
                    MATCH (g:Gene {symbol: $sym})-[e:EXPRESSES_IN]->(a:Anatomy)
                    RETURN a.name, e.expression_level
                """, sym=gene_symbol).data()
                return {"gene": gene_symbol, "anatomical_expression": effects}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_disease_anatomy(self, disease: str) -> Dict[str, Any]:
        try:
            with self.db_manager.get_neo4j_session() as session:
                matches = session.run("""
                    MATCH (d:Disease {name: $dis})-[r]-(a:Anatomy)
                    RETURN a.name, type(r)
                """, dis=disease).data()
                return {"disease": disease, "anatomical_impact": matches}
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_organ_summary(self, analysis: Dict) -> str:
        organ = analysis["organ_name"]
        dbs = len(analysis["databases_queried"])
        return f"Organ {organ} analyzed across {dbs} databases. Found anatomical structures and genetic connections."
