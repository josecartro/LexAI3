"""
Ontology Analyzer for LexAPI_Anatomics
Handles HPO normalization, MONDO disease mapping, and UBERON graph traversal
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager


class OntologyAnalyzer:
    """Ontology-based analysis using Neo4j for HPO, MONDO, UBERON"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
        
        # Common symptom to HPO term mappings for normalization
        self.symptom_to_hpo = {
            # Neurological
            "seizures": {"id": "HP:0001250", "name": "Seizure"},
            "seizure": {"id": "HP:0001250", "name": "Seizure"},
            "epilepsy": {"id": "HP:0001250", "name": "Seizure"},
            "hypotonia": {"id": "HP:0001252", "name": "Muscular hypotonia"},
            "muscle weakness": {"id": "HP:0001324", "name": "Muscle weakness"},
            "intellectual disability": {"id": "HP:0001249", "name": "Intellectual disability"},
            "developmental delay": {"id": "HP:0001263", "name": "Global developmental delay"},
            "spasticity": {"id": "HP:0001257", "name": "Spasticity"},
            "ataxia": {"id": "HP:0001251", "name": "Ataxia"},
            "tremor": {"id": "HP:0001337", "name": "Tremor"},
            "neuropathy": {"id": "HP:0009830", "name": "Peripheral neuropathy"},
            
            # Growth/Development
            "short stature": {"id": "HP:0004322", "name": "Short stature"},
            "tall stature": {"id": "HP:0000098", "name": "Tall stature"},
            "obesity": {"id": "HP:0001513", "name": "Obesity"},
            "failure to thrive": {"id": "HP:0001508", "name": "Failure to thrive"},
            
            # Sensory
            "hearing loss": {"id": "HP:0000365", "name": "Hearing impairment"},
            "deafness": {"id": "HP:0000365", "name": "Hearing impairment"},
            "vision loss": {"id": "HP:0000505", "name": "Visual impairment"},
            "blindness": {"id": "HP:0000505", "name": "Visual impairment"},
            
            # Cardiovascular
            "cardiac arrhythmia": {"id": "HP:0011675", "name": "Arrhythmia"},
            "arrhythmia": {"id": "HP:0011675", "name": "Arrhythmia"},
            "hypertension": {"id": "HP:0000822", "name": "Hypertension"},
            "cardiomyopathy": {"id": "HP:0001638", "name": "Cardiomyopathy"},
            "heart failure": {"id": "HP:0001635", "name": "Congestive heart failure"},
            
            # Renal
            "kidney stones": {"id": "HP:0000787", "name": "Nephrolithiasis"},
            "nephrolithiasis": {"id": "HP:0000787", "name": "Nephrolithiasis"},
            "kidney cysts": {"id": "HP:0000107", "name": "Renal cyst"},
            "renal cysts": {"id": "HP:0000107", "name": "Renal cyst"},
            "polycystic kidney": {"id": "HP:0000113", "name": "Polycystic kidney dysplasia"},
            "proteinuria": {"id": "HP:0000093", "name": "Proteinuria"},
            
            # Endocrine
            "thyroid nodule": {"id": "HP:0002890", "name": "Thyroid nodule"},
            "goiter": {"id": "HP:0000853", "name": "Goiter"},
            "pheochromocytoma": {"id": "HP:0002666", "name": "Pheochromocytoma"},
            "medullary thyroid carcinoma": {"id": "HP:0002668", "name": "Medullary thyroid carcinoma"},
            "hyperthyroidism": {"id": "HP:0000836", "name": "Hyperthyroidism"},
            "hypothyroidism": {"id": "HP:0000821", "name": "Hypothyroidism"},
            "diabetes": {"id": "HP:0000819", "name": "Diabetes mellitus"},
            "hypercalcemia": {"id": "HP:0003072", "name": "Hypercalcemia"},
            "hypocalcemia": {"id": "HP:0002901", "name": "Hypocalcemia"},
            
            # Gastrointestinal
            "hepatomegaly": {"id": "HP:0002240", "name": "Hepatomegaly"},
            "splenomegaly": {"id": "HP:0001744", "name": "Splenomegaly"},
            "colon cancer": {"id": "HP:0003003", "name": "Colon cancer"},
            "colorectal cancer": {"id": "HP:0003003", "name": "Colon cancer"},
            
            # Musculoskeletal
            "scoliosis": {"id": "HP:0002650", "name": "Scoliosis"},
            "joint hypermobility": {"id": "HP:0001382", "name": "Joint hypermobility"},
            "osteoporosis": {"id": "HP:0000939", "name": "Osteoporosis"},
            
            # Dermatological
            "cafe au lait spots": {"id": "HP:0000957", "name": "Cafe-au-lait spot"},
            "hyperpigmentation": {"id": "HP:0000953", "name": "Hyperpigmentation of the skin"},
            
            # Hematological
            "anemia": {"id": "HP:0001903", "name": "Anemia"},
            "thrombocytopenia": {"id": "HP:0001873", "name": "Thrombocytopenia"},
            
            # Cancer-related
            "breast cancer": {"id": "HP:0003002", "name": "Breast carcinoma"},
            "ovarian cancer": {"id": "HP:0100615", "name": "Ovarian neoplasm"},
            "endometrial cancer": {"id": "HP:0012114", "name": "Endometrial carcinoma"},
        }
    
    def normalize_phenotype(self, phenotype_text: str) -> Dict[str, Any]:
        """
        Normalize a free-text phenotype description to HPO term(s)
        
        Args:
            phenotype_text: Free text like "kidney cysts" or "seizures"
            
        Returns:
            Normalized HPO term(s) with ID and name
        """
        result = {
            "input": phenotype_text,
            "timestamp": datetime.now().isoformat(),
            "normalized_terms": [],
            "neo4j_matches": [],
            "confidence": "low"
        }
        
        # First check our local mapping (fast lookup)
        text_lower = phenotype_text.lower().strip()
        
        if text_lower in self.symptom_to_hpo:
            match = self.symptom_to_hpo[text_lower]
            result["normalized_terms"].append({
                "hpo_id": match["id"],
                "hpo_name": match["name"],
                "match_type": "exact",
                "confidence": 1.0
            })
            result["confidence"] = "high"
        
        # Also check for partial matches
        for symptom, hpo_data in self.symptom_to_hpo.items():
            if symptom in text_lower or text_lower in symptom:
                if not any(t["hpo_id"] == hpo_data["id"] for t in result["normalized_terms"]):
                    result["normalized_terms"].append({
                        "hpo_id": hpo_data["id"],
                        "hpo_name": hpo_data["name"],
                        "match_type": "partial",
                        "confidence": 0.7
                    })
                    if result["confidence"] == "low":
                        result["confidence"] = "medium"
        
        # Query Neo4j for additional matches
        try:
            neo4j_matches = self._query_hpo_neo4j(phenotype_text)
            result["neo4j_matches"] = neo4j_matches
            
            # Add Neo4j matches that aren't already in our results
            for match in neo4j_matches:
                if not any(t["hpo_id"] == match.get("id") for t in result["normalized_terms"]):
                    result["normalized_terms"].append({
                        "hpo_id": match.get("id", ""),
                        "hpo_name": match.get("name", ""),
                        "match_type": "neo4j_search",
                        "confidence": 0.6
                    })
        except Exception as e:
            result["neo4j_error"] = str(e)
        
        return result
    
    def _query_hpo_neo4j(self, phenotype_text: str) -> List[Dict]:
        """Query Neo4j for HPO terms matching the phenotype text"""
        try:
            with self.db_manager.get_neo4j_session() as session:
                # Search for HPO nodes matching the text
                results = session.run("""
                    MATCH (h)
                    WHERE (h:HPO OR h:Phenotype OR h:Disease)
                    AND toLower(h.name) CONTAINS toLower($text)
                    RETURN h.id as id, h.name as name, labels(h) as labels
                    LIMIT 10
                """, text=phenotype_text).data()
                
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def traverse_uberon_hierarchy(self, structure_name: str, direction: str = "both", max_depth: int = 3) -> Dict[str, Any]:
        """
        Traverse UBERON anatomical hierarchy using part-of and is-a relationships
        
        Args:
            structure_name: Anatomical structure name (e.g., "kidney", "heart")
            direction: "up" (parents), "down" (children), or "both"
            max_depth: Maximum traversal depth
            
        Returns:
            Hierarchical structure with parent/child relationships
        """
        result = {
            "structure": structure_name,
            "timestamp": datetime.now().isoformat(),
            "hierarchy": {
                "parents": [],      # is-a and part-of upward
                "children": [],     # is-a and part-of downward
                "siblings": [],     # same parent
                "related": []       # other relationships
            },
            "uberon_id": None,
            "traversal_depth": max_depth
        }
        
        try:
            with self.db_manager.get_neo4j_session() as session:
                # First find the structure
                structure_match = session.run("""
                    MATCH (a:Anatomy)
                    WHERE toLower(a.name) CONTAINS toLower($name)
                    RETURN a.id as id, a.name as name
                    LIMIT 1
                """, name=structure_name).single()
                
                if structure_match:
                    result["uberon_id"] = structure_match["id"]
                    result["matched_name"] = structure_match["name"]
                    
                    # Traverse upward (parents via is-a and part-of)
                    if direction in ["up", "both"]:
                        parents = session.run("""
                            MATCH (child:Anatomy)-[r:IS_A|PART_OF*1..3]->(parent:Anatomy)
                            WHERE toLower(child.name) CONTAINS toLower($name)
                            RETURN DISTINCT parent.id as id, parent.name as name, 
                                   type(r[0]) as relationship, length(r) as depth
                            ORDER BY depth
                            LIMIT 20
                        """, name=structure_name).data()
                        result["hierarchy"]["parents"] = parents
                    
                    # Traverse downward (children)
                    if direction in ["down", "both"]:
                        children = session.run("""
                            MATCH (parent:Anatomy)<-[r:IS_A|PART_OF*1..3]-(child:Anatomy)
                            WHERE toLower(parent.name) CONTAINS toLower($name)
                            RETURN DISTINCT child.id as id, child.name as name,
                                   type(r[0]) as relationship, length(r) as depth
                            ORDER BY depth
                            LIMIT 20
                        """, name=structure_name).data()
                        result["hierarchy"]["children"] = children
                    
                    # Find siblings (same parent)
                    siblings = session.run("""
                        MATCH (a:Anatomy)-[:IS_A|PART_OF]->(parent:Anatomy)<-[:IS_A|PART_OF]-(sibling:Anatomy)
                        WHERE toLower(a.name) CONTAINS toLower($name)
                        AND a <> sibling
                        RETURN DISTINCT sibling.id as id, sibling.name as name, parent.name as common_parent
                        LIMIT 10
                    """, name=structure_name).data()
                    result["hierarchy"]["siblings"] = siblings
                    
                    # Find other related structures
                    related = session.run("""
                        MATCH (a:Anatomy)-[r]-(b:Anatomy)
                        WHERE toLower(a.name) CONTAINS toLower($name)
                        AND NOT type(r) IN ['IS_A', 'PART_OF']
                        RETURN DISTINCT b.id as id, b.name as name, type(r) as relationship
                        LIMIT 10
                    """, name=structure_name).data()
                    result["hierarchy"]["related"] = related
                else:
                    result["error"] = "Structure not found in UBERON"
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def map_phenotype_to_diseases(self, hpo_terms: List[str]) -> Dict[str, Any]:
        """
        Map HPO phenotype terms to MONDO diseases
        
        Args:
            hpo_terms: List of HPO IDs (e.g., ["HP:0001250", "HP:0001252"]) or symptom names
            
        Returns:
            Ranked list of diseases with supporting phenotype matches
        """
        result = {
            "input_phenotypes": hpo_terms,
            "timestamp": datetime.now().isoformat(),
            "diseases": [],
            "gene_associations": [],
            "phenotype_coverage": {}
        }
        
        # Normalize terms if they're symptom names
        normalized_hpo = []
        for term in hpo_terms:
            if term.startswith("HP:"):
                normalized_hpo.append(term)
            else:
                norm_result = self.normalize_phenotype(term)
                if norm_result["normalized_terms"]:
                    normalized_hpo.append(norm_result["normalized_terms"][0]["hpo_id"])
        
        result["normalized_hpo_ids"] = normalized_hpo
        
        try:
            with self.db_manager.get_neo4j_session() as session:
                # Find diseases associated with these phenotypes
                if normalized_hpo:
                    diseases = session.run("""
                        MATCH (p)-[:PHENOTYPE_OF|ASSOCIATED_WITH]-(d:Disease)
                        WHERE p.id IN $hpo_ids OR p.name IN $hpo_terms
                        WITH d, collect(DISTINCT p.name) as matching_phenotypes, count(DISTINCT p) as match_count
                        RETURN d.id as disease_id, d.name as disease_name, 
                               matching_phenotypes, match_count
                        ORDER BY match_count DESC
                        LIMIT 15
                    """, hpo_ids=normalized_hpo, hpo_terms=hpo_terms).data()
                    
                    result["diseases"] = diseases
                    
                    # Get genes associated with top diseases
                    if diseases:
                        top_diseases = [d["disease_name"] for d in diseases[:5] if d.get("disease_name")]
                        genes = session.run("""
                            MATCH (g:Gene)-[:CAUSES|ASSOCIATED_WITH]-(d:Disease)
                            WHERE d.name IN $diseases
                            RETURN DISTINCT g.symbol as gene, d.name as disease
                            LIMIT 20
                        """, diseases=top_diseases).data()
                        
                        result["gene_associations"] = genes
                        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_anatomy_for_phenotype(self, phenotype: str) -> Dict[str, Any]:
        """
        Get anatomical structures associated with a phenotype
        
        Args:
            phenotype: HPO ID or symptom name
            
        Returns:
            List of affected anatomical structures
        """
        result = {
            "phenotype": phenotype,
            "timestamp": datetime.now().isoformat(),
            "affected_anatomy": [],
            "tissue_types": []
        }
        
        # Normalize if needed
        if not phenotype.startswith("HP:"):
            norm = self.normalize_phenotype(phenotype)
            if norm["normalized_terms"]:
                phenotype = norm["normalized_terms"][0]["hpo_id"]
                result["normalized_hpo"] = phenotype
        
        try:
            with self.db_manager.get_neo4j_session() as session:
                # Find anatomy connected to this phenotype
                anatomy = session.run("""
                    MATCH (p)-[:AFFECTS|LOCATED_IN|MANIFESTS_IN]-(a:Anatomy)
                    WHERE p.id = $hpo OR toLower(p.name) CONTAINS toLower($hpo)
                    RETURN DISTINCT a.id as id, a.name as name, labels(a) as types
                    LIMIT 20
                """, hpo=phenotype).data()
                
                result["affected_anatomy"] = anatomy
                
        except Exception as e:
            result["error"] = str(e)
        
        return result

