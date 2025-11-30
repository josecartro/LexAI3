"""
Safe Pathway Coverage Check
Simple, safe script to check gene-pathway connections
"""

import duckdb
import time
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("Starting SAFE pathway coverage check")
    log("Will check gene-pathway connections carefully")
    
    try:
        db_path = "../../data/databases/genomic_knowledge/genomic_knowledge.duckdb"
        log(f"Connecting to database: {db_path}")
        
        conn = duckdb.connect(db_path, read_only=True)
        log("Database connection successful")
        
        # Step 1: Check total coverage (safe, fast query)
        log("\nStep 1: Checking total coverage...")
        total_genes = conn.execute("SELECT COUNT(DISTINCT gene_symbol) FROM kegg_gene_pathway_links WHERE gene_symbol IS NOT NULL").fetchone()[0]
        total_pathways = conn.execute("SELECT COUNT(DISTINCT pathway_id) FROM kegg_gene_pathway_links").fetchone()[0]
        
        log(f"Total genes with pathway connections: {total_genes:,}")
        log(f"Total pathways available: {total_pathways:,}")
        
        # Step 2: Check specific disease genes (safe, individual queries)
        log("\nStep 2: Checking disease genes...")
        disease_genes = ["BRCA1", "BRCA2", "TP53", "CFTR", "APOE"]
        
        for gene in disease_genes:
            log(f"Checking {gene}...")
            try:
                count = conn.execute("SELECT COUNT(*) FROM kegg_gene_pathway_links WHERE gene_symbol = ?", [gene]).fetchone()[0]
                log(f"  {gene}: {count} pathway connections")
                
                if count > 0:
                    # Get sample pathway (safe, limited query)
                    sample = conn.execute("SELECT pathway_name FROM kegg_gene_pathway_links WHERE gene_symbol = ? LIMIT 1", [gene]).fetchone()
                    if sample:
                        log(f"    Sample pathway: {sample[0]}")
                
                # Small delay to be safe
                time.sleep(0.5)
                
            except Exception as e:
                log(f"  {gene}: ERROR - {e}")
        
        # Step 3: Sample pathways (safe, limited query)
        log("\nStep 3: Sample pathways available...")
        try:
            sample_pathways = conn.execute("""
                SELECT pathway_name, COUNT(*) as gene_count
                FROM kegg_gene_pathway_links
                GROUP BY pathway_name
                ORDER BY gene_count DESC
                LIMIT 5
            """).fetchall()
            
            for pathway, gene_count in sample_pathways:
                log(f"  {pathway}: {gene_count} genes")
                
        except Exception as e:
            log(f"Sample pathways ERROR: {e}")
        
        conn.close()
        log("Database connection closed safely")
        
        log("\nSafe analysis complete - no system stress")
        
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
