"""
Safe GTEx eQTL Data Check
Check variant-expression data safely before integration
"""

import duckdb
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    log("Checking GTEx eQTL data safely")
    
    try:
        conn = duckdb.connect("../data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Check total coverage
        total_variants = conn.execute("SELECT COUNT(DISTINCT variant_id) FROM gtex_v10_eqtl_associations").fetchone()[0]
        total_genes = conn.execute("SELECT COUNT(DISTINCT gene_symbol) FROM gtex_v10_eqtl_associations WHERE gene_symbol IS NOT NULL").fetchone()[0]
        total_tissues = conn.execute("SELECT COUNT(DISTINCT tissue_type) FROM gtex_v10_eqtl_associations").fetchone()[0]
        
        log(f"GTEx eQTL coverage:")
        log(f"  Variants with expression effects: {total_variants:,}")
        log(f"  Genes with expression data: {total_genes:,}")
        log(f"  Tissues analyzed: {total_tissues:,}")
        
        # Check specific variants
        log(f"\nChecking specific variants:")
        test_variants = ["rs7412", "rs429358", "rs4680"]
        
        for variant in test_variants:
            # Try different variant ID formats
            formats_to_try = [variant, variant.replace('rs', '')]
            found = False
            
            for variant_format in formats_to_try:
                try:
                    count = conn.execute("SELECT COUNT(*) FROM gtex_v10_eqtl_associations WHERE variant_id LIKE ?", [f"%{variant_format}%"]).fetchone()[0]
                    if count > 0:
                        log(f"  {variant}: {count} expression effects found")
                        found = True
                        break
                except:
                    pass
            
            if not found:
                log(f"  {variant}: No expression effects found")
        
        # Check tissue types
        log(f"\nTissue types available:")
        tissues = conn.execute("SELECT DISTINCT tissue_type FROM gtex_v10_eqtl_associations ORDER BY tissue_type LIMIT 10").fetchall()
        for tissue, in tissues:
            log(f"  {tissue}")
        
        # Check sample data structure
        log(f"\nSample eQTL data:")
        sample = conn.execute("SELECT * FROM gtex_v10_eqtl_associations LIMIT 1").fetchone()
        if sample:
            log(f"  Sample: variant_id={sample[0]}, gene={sample[2]}, tissue={sample[3]}, effect={sample[8]}")
        
        conn.close()
        log("Safe GTEx check complete")
        
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
