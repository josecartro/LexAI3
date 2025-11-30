"""
Simple GraphQL Implementation for LexAPI_Anatomics
Working GraphQL queries for anatomical data
"""

import strawberry
from typing import List, Optional
from neo4j import GraphDatabase
from pathlib import Path

# Neo4j connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "000neo4j")

def get_neo4j_data(query, params=None):
    """Get data from Neo4j database"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    with driver.session() as session:
        if params:
            result = session.run(query, params).data()
        else:
            result = session.run(query).data()
    driver.close()
    return result

@strawberry.type
class AnatomyStructure:
    name: str
    anatomy_id: Optional[str] = None
    structure_type: Optional[str] = None

@strawberry.type
class GeneExpression:
    gene: str
    tissue: str
    expression_level: str

@strawberry.type
class Disease:
    name: str
    disease_type: Optional[str] = None

@strawberry.type
class Query:
    
    @strawberry.field
    def anatomy(self, name: str) -> Optional[AnatomyStructure]:
        """Get anatomy structure by name"""
        try:
            results = get_neo4j_data("""
                MATCH (a:Anatomy) 
                WHERE toLower(a.name) CONTAINS toLower($name)
                RETURN a.name, a.id, labels(a)[0] as type
                LIMIT 1
            """, {"name": name})
            
            if results:
                result = results[0]
                return AnatomyStructure(
                    name=result["a.name"],
                    anatomy_id=result["a.id"],
                    structure_type=result["type"]
                )
            return None
            
        except Exception as e:
            print(f"GraphQL anatomy error: {e}")
            return None
    
    @strawberry.field
    def gene_expression_in_tissue(self, tissue: str) -> List[GeneExpression]:
        """Get genes expressed in specific tissue"""
        try:
            results = get_neo4j_data("""
                MATCH (g:Gene)-[e:EXPRESSES_IN]->(a:Anatomy)
                WHERE toLower(a.name) CONTAINS toLower($tissue)
                RETURN g.symbol as gene, a.name as tissue, e.expression_level as level
                LIMIT 20
            """, {"tissue": tissue})
            
            return [
                GeneExpression(
                    gene=result["gene"],
                    tissue=result["tissue"],
                    expression_level=result["level"]
                )
                for result in results
            ]
            
        except Exception as e:
            print(f"GraphQL gene expression error: {e}")
            return []
    
    @strawberry.field
    def anatomy_structures(self, organ: str) -> List[AnatomyStructure]:
        """Get all anatomy structures for an organ"""
        try:
            results = get_neo4j_data("""
                MATCH (a:Anatomy) 
                WHERE toLower(a.name) CONTAINS toLower($organ)
                RETURN a.name, a.id, labels(a)[0] as type
                LIMIT 15
            """, {"organ": organ})
            
            return [
                AnatomyStructure(
                    name=result["a.name"],
                    anatomy_id=result["a.id"],
                    structure_type=result["type"]
                )
                for result in results
            ]
            
        except Exception as e:
            print(f"GraphQL anatomy structures error: {e}")
            return []
    
    @strawberry.field
    def diseases_affecting_organ(self, organ: str) -> List[Disease]:
        """Get diseases that affect specific organ"""
        try:
            results = get_neo4j_data("""
                MATCH (d:Disease)
                WHERE toLower(d.name) CONTAINS toLower($organ)
                RETURN DISTINCT d.name, labels(d)[0] as type
                LIMIT 10
            """, {"organ": organ})
            
            return [
                Disease(
                    name=result["d.name"],
                    disease_type=result["type"]
                )
                for result in results
            ]
            
        except Exception as e:
            print(f"GraphQL diseases error: {e}")
            return []

# Create schema
schema = strawberry.Schema(query=Query)

