"""
Variant Analyzer for LexAPI_Genomics
Handles comprehensive variant analysis logic using ClickHouse
"""

from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.clickhouse_database_manager import ClickHouseDatabaseManager

class VariantAnalyzer:
    """Comprehensive variant analysis across multiple databases (ClickHouse)"""
    
    def __init__(self):
        self.db_manager = ClickHouseDatabaseManager()
    
    def analyze_variant_comprehensive(self, variant_id: str) -> Dict[str, Any]:
        """Complete variant analysis across all databases"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing variant {variant_id} comprehensively...")
        
        analysis = {
            "variant_id": variant_id,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": [],
            "genomic_data": {},
            "expression_data": {},
            "causal_connections": {},
            "clinical_significance": {},
            "comprehensive_summary": ""
        }
        
        # Step 1: Query genomic knowledge database (ClickHouse)
        # We assume there's a method or query to get single variant details
        # The manager has query_variants_by_gene but maybe we need query_variant_by_id
        # Let's use a custom query here via client if needed, or add method to manager.
        # Adding method to manager would be cleaner but I can access client directly.
        
        client = self.db_manager.get_clickhouse_client()
        
        # 1. Variant Info
        try:
            # Handle rs prefix if needed - try exact match first, then stripped
            stripped_id = variant_id.replace('rs', '')
            
            var_query = f"""
            SELECT rsid, gene_symbol, clinical_significance, disease_name, 
                   chrom, pos, ref, alt
            FROM genomics_db.clinvar_variants
            WHERE rsid = '{variant_id}' OR rsid = '{stripped_id}'
            LIMIT 1
            """
            res = client.query(var_query).result_rows
            if res:
                analysis["genomic_data"] = {
                    "rsid": res[0][0],
                    "gene_symbol": res[0][1],
                    "clinical_significance": res[0][2],
                    "associated_disease": res[0][3],
                    "chromosome": res[0][4],
                    "position": res[0][5],
                    "ref_allele": res[0][6],
                    "alt_allele": res[0][7],
                    "data_source": "clinvar (clickhouse)"
                }
                analysis["databases_queried"].append("genomics_db.clinvar_variants")
        except Exception as e:
            print(f"Error querying variant: {e}")

        gene_symbol = analysis["genomic_data"].get("gene_symbol")

        # Step 2: Query expression (GTEx eQTL)
        if gene_symbol:
            # We can use the gene query from manager, or specific variant eqtl query
            # Let's try specific variant query if we have table
            try:
                eqtl_query = f"""
                SELECT tissue, slope, pval_beta
                FROM expression_db.gtex_eqtl
                WHERE variant_id = '{variant_id}'
                ORDER BY abs(slope) DESC
                LIMIT 10
                """
                eqtl_res = client.query(eqtl_query).result_rows
                if eqtl_res:
                    analysis["expression_effects"] = [
                        {"tissue": r[0], "effect_size": r[1], "p_value": r[2]}
                        for r in eqtl_res
                    ]
                    analysis["databases_queried"].append("expression_db.gtex_eqtl")
            except Exception as e:
                print(f"Error querying eQTL: {e}")
        
        # Step 3: SpliceAI
        try:
            splice_res = self.db_manager.query_splice_predictions(gene_symbol, 0.2) if gene_symbol else []
            # Filter for this variant if possible, or just use gene context
            # The manager method returns list of dicts
            variant_splice = [s for s in splice_res if s.get("variant_id") == variant_id]
            if variant_splice:
                analysis["splicing_predictions"] = variant_splice[0]
                analysis["databases_queried"].append("genomics_db.spliceai_predictions")
        except Exception as e:
            print(f"Error querying SpliceAI: {e}")

        # Step 4: AlphaFold (Protein)
        if gene_symbol:
            try:
                prot_res = self.db_manager.query_protein_structures(gene_symbol)
                if prot_res:
                    analysis["protein_structure_effects"] = prot_res
                    analysis["databases_queried"].append("proteins_db.alphafold_structures")
            except Exception as e:
                print(f"Error querying proteins: {e}")
        
        # Step 5: Neo4j Causal
        if gene_symbol:
            try:
                with self.db_manager.get_neo4j_session() as session:
                    result = session.run("""
                        MATCH (g:Gene {symbol: $gene})
                        OPTIONAL MATCH (g)-[:ASSOCIATED_WITH]->(d:Disease)
                        RETURN collect(d.name) as diseases
                    """, gene=gene_symbol).single()
                    if result:
                        analysis["causal_connections"] = {"associated_diseases": result["diseases"]}
                analysis["databases_queried"].append("neo4j")
            except Exception as e:
                print(f"Error querying Neo4j: {e}")
        
        # Generate summaries
        analysis["clinical_significance"] = self._generate_clinical_assessment(analysis)
        analysis["comprehensive_summary"] = self._generate_variant_summary(analysis)
        
        return analysis
    
    def _generate_clinical_assessment(self, analysis: Dict) -> Dict[str, Any]:
        genomic = analysis.get("genomic_data", {})
        assessment = {"risk_level": "unknown", "clinical_action": "unknown", "confidence": "low"}
        
        if genomic.get("clinical_significance"):
            sig = genomic["clinical_significance"].lower()
            if "pathogenic" in sig:
                assessment.update({"risk_level": "high", "clinical_action": "counseling_recommended", "confidence": "high"})
            elif "benign" in sig:
                assessment.update({"risk_level": "low", "clinical_action": "none", "confidence": "high"})
            elif "uncertain" in sig:
                assessment.update({"risk_level": "uncertain", "clinical_action": "monitor", "confidence": "medium"})
        return assessment
    
    def _generate_variant_summary(self, analysis: Dict) -> str:
        var_id = analysis.get("variant_id")
        gene = analysis.get("genomic_data", {}).get("gene_symbol", "Unknown")
        return f"Variant {var_id} (Gene: {gene}) analyzed across {len(analysis['databases_queried'])} databases."
    
    def analyze_variant_batch(self, variant_list: List[str]) -> Dict[str, Any]:
        results = []
        for v in variant_list:
            results.append(self.analyze_variant_comprehensive(v))
        return {
            "total": len(variant_list),
            "results": results
        }
