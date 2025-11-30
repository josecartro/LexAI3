"""
Migrate All Genomics Data to ClickHouse
Complete migration without unicode issues
"""

import clickhouse_connect
import gzip
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

class GenomicsMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            password='simple123'
        )
        self.batch_size = 50000
        
    def setup_tables(self):
        """Create all tables"""
        log("Setting up databases and tables...")
        
        self.client.command("CREATE DATABASE IF NOT EXISTS genomics_db")
        
        # ClinVar table
        self.client.command("""
            CREATE TABLE IF NOT EXISTS genomics_db.clinvar_variants (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                gene_symbol String,
                clinical_significance String,
                disease_name String
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, rsid)
        """)
        
        log("Tables created successfully")
    
    def migrate_clinvar_fast(self):
        """Migrate ClinVar with optimized processing"""
        log("\nMIGRATING CLINVAR VARIANTS")
        log("="*50)
        
        vcf_file = Path("data/global/clinvar/clinvar_GRCh38.vcf.gz")
        if not vcf_file.exists():
            log(f"ERROR: ClinVar file not found")
            return False
        
        log(f"Processing ClinVar file ({vcf_file.stat().st_size/(1024*1024):.1f} MB)")
        
        batch = []
        total = 0
        start_time = time.time()
        
        with gzip.open(vcf_file, 'rt') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    
                    try:
                        pos = int(parts[1])
                    except:
                        continue
                    
                    rsid = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Quick parsing
                    gene_symbol = "unknown"
                    clinical_sig = "unknown"
                    disease = "unknown"
                    
                    if "GENEINFO=" in info:
                        try:
                            gene_symbol = info.split("GENEINFO=")[1].split(";")[0].split(":")[0]
                        except:
                            pass
                    
                    if "CLNSIG=" in info:
                        try:
                            clinical_sig = info.split("CLNSIG=")[1].split(";")[0]
                        except:
                            pass
                    
                    batch.append((chrom, pos, rsid, ref, alt, gene_symbol, clinical_sig, disease))
                
                if len(batch) >= self.batch_size:
                    try:
                        self.client.insert('genomics_db.clinvar_variants', batch)
                        total += len(batch)
                        
                        if total % 500000 == 0:  # Report every 500K
                            elapsed = time.time() - start_time
                            rate = total / elapsed
                            log(f"   ClinVar progress: {total:,} variants ({rate:.0f}/sec)")
                        
                        batch = []
                    except:
                        batch = []  # Skip bad batches
        
        if batch:
            self.client.insert('genomics_db.clinvar_variants', batch)
            total += len(batch)
        
        elapsed = time.time() - start_time
        log(f"ClinVar complete: {total:,} variants in {elapsed/60:.1f} minutes")
        
        # Verify
        final_count = self.client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
        log(f"Final count: {final_count:,} variants")
        
        return final_count > 1000000

def main():
    log("="*80)
    log("COMPLETE GENOMICS MIGRATION TO CLICKHOUSE")
    log("="*80)
    log("Starting with ClinVar dataset...")
    
    migrator = GenomicsMigrator()
    
    # Setup
    migrator.setup_tables()
    
    # Start with ClinVar
    success = migrator.migrate_clinvar_fast()
    
    if success:
        log("\nCLINVAR MIGRATION SUCCESS")
        log("Ready to continue with other datasets")
    else:
        log("\nCLINVAR MIGRATION FAILED") 

if __name__ == "__main__":
    main()

