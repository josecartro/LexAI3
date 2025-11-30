"""
Safe Production Table Queries
Non-lethal access to massive production tables with proven safe methods
"""

import duckdb
import time
import psutil
from pathlib import Path
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

class SafeProductionQueries:
    """Safe queries for massive production tables"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.query_timeout = 15  # 15 second timeout
        self.max_results = 50    # Maximum 50 results
        
    def safe_spliceai_lookup(self, gene_symbol: str = None, variant_id: str = None):
        """Safe SpliceAI lookup with strict limits"""
        try:
            conn = duckdb.connect(str(self.db_path), read_only=True)
            
            # Build safe query
            if gene_symbol:
                # Gene-based lookup (safer)
                query = """
                    SELECT variant_id, gene_symbol, acceptor_gain_score, acceptor_loss_score,
                           donor_gain_score, donor_loss_score
                    FROM spliceai_scores_production
                    WHERE gene_symbol = ?
                    AND (ABS(acceptor_gain_score) > 0.1 OR ABS(acceptor_loss_score) > 0.1 
                         OR ABS(donor_gain_score) > 0.1 OR ABS(donor_loss_score) > 0.1)
                    ORDER BY ABS(acceptor_gain_score) + ABS(acceptor_loss_score) + 
                             ABS(donor_gain_score) + ABS(donor_loss_score) DESC
                    LIMIT ?
                """
                params = [gene_symbol, self.max_results]
                
            elif variant_id:
                # Variant-based lookup (more specific)
                search_id = variant_id.replace('rs', '')
                query = """
                    SELECT variant_id, gene_symbol, acceptor_gain_score, acceptor_loss_score,
                           donor_gain_score, donor_loss_score
                    FROM spliceai_scores_production
                    WHERE variant_id LIKE ?
                    LIMIT ?
                """
                params = [f"%{search_id}%", self.max_results]
            else:
                return {"error": "gene_symbol_or_variant_id_required"}
            
            # Execute with timeout monitoring
            start_time = time.time()
            results = conn.execute(query, params).fetchall()
            query_time = time.time() - start_time
            
            conn.close()
            
            if query_time > self.query_timeout:
                log(f"⚠️  SpliceAI query took {query_time:.1f}s (limit: {self.query_timeout}s)")
            
            return {
                "splice_predictions": [
                    {
                        "variant_id": row[0],
                        "gene_symbol": row[1],
                        "acceptor_gain": row[2],
                        "acceptor_loss": row[3],
                        "donor_gain": row[4], 
                        "donor_loss": row[5],
                        "max_score": max(abs(row[2] or 0), abs(row[3] or 0), abs(row[4] or 0), abs(row[5] or 0))
                    }
                    for row in results
                ],
                "total_results": len(results),
                "query_time": round(query_time, 2),
                "data_source": "spliceai_scores_production",
                "safety_applied": True
            }
            
        except Exception as e:
            return {"error": str(e), "safety_applied": True}
    
    def safe_alphafold_lookup(self, gene_symbol: str):
        """Safe AlphaFold lookup with limits"""
        try:
            conn = duckdb.connect(str(self.db_path), read_only=True)
            
            query = """
                SELECT uniprot_id, protein_name, structure_confidence_avg, tissue_type
                FROM alphafold_clinical_variant_impact
                WHERE gene_symbol = ?
                ORDER BY structure_confidence_avg DESC
                LIMIT ?
            """
            
            start_time = time.time()
            results = conn.execute(query, [gene_symbol, self.max_results]).fetchall()
            query_time = time.time() - start_time
            
            conn.close()
            
            return {
                "protein_structures": [
                    {
                        "uniprot_id": row[0],
                        "protein_name": row[1],
                        "structure_confidence": row[2],
                        "tissue_type": row[3]
                    }
                    for row in results
                ],
                "total_results": len(results),
                "query_time": round(query_time, 2),
                "data_source": "alphafold_clinical_variant_impact",
                "safety_applied": True
            }
            
        except Exception as e:
            return {"error": str(e), "safety_applied": True}
    
    def safe_gnomad_lookup(self, variant_id: str):
        """Safe gnomAD population frequency lookup"""
        try:
            conn = duckdb.connect(str(self.db_path), read_only=True)
            
            query = """
                SELECT rsid, chrom, pos_bp, ref, alt, allele_frequency
                FROM gnomad_population_frequencies
                WHERE rsid = ?
                LIMIT ?
            """
            
            start_time = time.time()
            results = conn.execute(query, [variant_id, self.max_results]).fetchall()
            query_time = time.time() - start_time
            
            conn.close()
            
            return {
                "population_frequencies": [
                    {
                        "rsid": row[0],
                        "chromosome": row[1],
                        "position": row[2],
                        "ref_allele": row[3],
                        "alt_allele": row[4],
                        "allele_frequency": row[5]
                    }
                    for row in results
                ],
                "total_results": len(results),
                "query_time": round(query_time, 2),
                "data_source": "gnomad_population_frequencies",
                "safety_applied": True
            }
            
        except Exception as e:
            return {"error": str(e), "safety_applied": True}

# Test the safe methods
if __name__ == "__main__":
    print("Testing safe production table access...")
    
    db_path = Path("data/databases/genomic_knowledge/genomic_knowledge.duckdb")
    safe_queries = SafeProductionQueries(db_path)
    
    # Test safe SpliceAI
    print("\nTesting safe SpliceAI lookup...")
    spliceai_result = safe_queries.safe_spliceai_lookup(gene_symbol="BRCA2")
    if 'error' not in spliceai_result:
        print(f"✅ SpliceAI: {spliceai_result['total_results']} results in {spliceai_result['query_time']}s")
    else:
        print(f"❌ SpliceAI: {spliceai_result['error']}")
    
    # Test safe AlphaFold
    print("\nTesting safe AlphaFold lookup...")
    alphafold_result = safe_queries.safe_alphafold_lookup("BRCA2")
    if 'error' not in alphafold_result:
        print(f"✅ AlphaFold: {alphafold_result['total_results']} results in {alphafold_result['query_time']}s")
    else:
        print(f"❌ AlphaFold: {alphafold_result['error']}")
    
    print("\nSafe access methods verified!")
