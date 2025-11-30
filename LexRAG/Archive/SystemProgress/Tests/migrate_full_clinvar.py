"""
Migrate FULL ClinVar Dataset to ClickHouse
Process the complete ClinVar VCF file (all variants)
"""

import clickhouse_connect
import gzip
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def migrate_full_clinvar():
    """Migrate complete ClinVar VCF to ClickHouse"""
    log("MIGRATING FULL CLINVAR DATASET TO CLICKHOUSE")
    log("="*70)
    log("WARNING: This will process the ENTIRE ClinVar VCF file")
    
    try:
        # Connect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: ClickHouse connected")
        
        # Check file
        vcf_file = Path("data/global/clinvar/clinvar_GRCh38.vcf.gz")
        if not vcf_file.exists():
            log(f"ERROR: File not found: {vcf_file}")
            return False
        
        file_size_mb = vcf_file.stat().st_size / (1024*1024)
        log(f"SUCCESS: ClinVar VCF found ({file_size_mb:.1f} MB)")
        
        # Drop and recreate table for full data
        log("Preparing table for full dataset...")
        client.command("DROP TABLE IF EXISTS genomics_db.clinvar_full")
        
        create_table = """
            CREATE TABLE genomics_db.clinvar_full (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                gene_symbol String,
                clinical_significance String,
                disease_name String,
                pathogenicity_score Float32
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, rsid)
        """
        
        client.command(create_table)
        log("SUCCESS: Full ClinVar table created")
        
        # Process FULL VCF file
        log("Processing COMPLETE ClinVar VCF file...")
        log("This may take several minutes...")
        
        variants_batch = []
        total_processed = 0
        batch_size = 10000  # Process in batches
        
        start_time = time.time()
        
        with gzip.open(vcf_file, 'rt') as f:
            for line_num, line in enumerate(f, 1):
                # Skip headers
                if line.startswith('#'):
                    continue
                
                # Process variant
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')  # Normalize chromosome
                    
                    try:
                        pos = int(parts[1])
                    except:
                        continue
                    
                    rsid = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Parse INFO field for gene and clinical data
                    gene_symbol = "unknown"
                    clinical_sig = "unknown" 
                    disease = "unknown"
                    pathogenicity = 0.0
                    
                    # Extract gene symbol
                    if "GENEINFO=" in info:
                        try:
                            gene_part = info.split("GENEINFO=")[1].split(";")[0]
                            gene_symbol = gene_part.split(":")[0]
                        except:
                            pass
                    
                    # Extract clinical significance
                    if "CLNSIG=" in info:
                        try:
                            clinical_sig = info.split("CLNSIG=")[1].split(";")[0].replace("_", " ")
                        except:
                            pass
                    
                    # Extract disease name
                    if "CLNDN=" in info:
                        try:
                            disease = info.split("CLNDN=")[1].split(";")[0]
                            disease = disease.replace("_", " ").replace("%2C", ",")[:200]  # Limit length
                        except:
                            pass
                    
                    # Simple pathogenicity scoring
                    if "Pathogenic" in clinical_sig:
                        pathogenicity = 0.9
                    elif "Likely_pathogenic" in clinical_sig:
                        pathogenicity = 0.7
                    elif "Benign" in clinical_sig:
                        pathogenicity = 0.1
                    
                    variants_batch.append((
                        chrom, pos, rsid, ref, alt, gene_symbol, 
                        clinical_sig, disease, pathogenicity
                    ))
                
                # Insert in batches
                if len(variants_batch) >= batch_size:
                    try:
                        client.insert('genomics_db.clinvar_full', variants_batch)
                        total_processed += len(variants_batch)
                        
                        current_time = time.time()
                        elapsed = current_time - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        
                        log(f"   Processed: {total_processed:,} variants ({rate:.0f}/sec)")
                        
                        variants_batch = []  # Reset batch
                        
                    except Exception as e:
                        log(f"   Batch insert error: {e}")
                        variants_batch = []  # Skip problematic batch
        
        # Insert final batch
        if variants_batch:
            client.insert('genomics_db.clinvar_full', variants_batch)
            total_processed += len(variants_batch)
        
        total_time = time.time() - start_time
        
        log(f"\nFULL CLINVAR MIGRATION COMPLETE:")
        log(f"Total variants processed: {total_processed:,}")
        log(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        log(f"Processing rate: {total_processed/total_time:.0f} variants/second")
        
        # Final performance test
        log("Testing final performance...")
        
        start = time.time()
        final_count = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_full").result_rows[0][0]
        count_time = time.time() - start
        
        log(f"Final count: {final_count:,} variants in {count_time:.4f}s")
        
        if count_time < 0.1:
            log("EXCELLENT: Full ClinVar dataset with sub-0.1s performance!")
        
        return True
        
    except Exception as e:
        log(f"ERROR: Full migration failed - {e}")
        return False

if __name__ == "__main__":
    success = migrate_full_clinvar()
    if success:
        print("FULL CLINVAR MIGRATION SUCCESS!")
    else:
        print("FULL CLINVAR MIGRATION FAILED")
