"""
Phase 2: Migrate dbSNP Common Variants to ClickHouse
Migrate dbSNP from original VCF file (4 GB)
"""

import clickhouse_connect
import gzip
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def migrate_dbsnp_variants():
    """Migrate dbSNP common variants from original VCF to ClickHouse"""
    log("PHASE 2: DBSNP COMMON VARIANTS TO CLICKHOUSE")
    log("="*70)
    
    try:
        # Connect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: ClickHouse connected")
        
        # Check source file
        vcf_file = Path("data/global/dbsnp/dbsnp156_common.vcf.gz")
        if not vcf_file.exists():
            log(f"ERROR: dbSNP VCF not found: {vcf_file}")
            return False
        
        file_size_mb = vcf_file.stat().st_size / (1024*1024)
        log(f"SUCCESS: dbSNP VCF found ({file_size_mb:.1f} MB)")
        
        # Create dbSNP table
        log("Creating dbSNP table...")
        client.command("DROP TABLE IF EXISTS genomics_db.dbsnp_common")
        
        create_table = """
            CREATE TABLE genomics_db.dbsnp_common (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                qual Float32,
                filter String,
                allele_frequency Float32,
                variant_class String,
                gene_info String
            ) ENGINE = MergeTree()
            ORDER BY (rsid, chrom, pos)
        """
        
        client.command(create_table)
        log("SUCCESS: dbSNP table created")
        
        # Process VCF file
        log("Processing dbSNP VCF file...")
        log("This is a 4 GB file - may take several minutes...")
        
        variants_batch = []
        total_processed = 0
        batch_size = 10000
        
        start_time = time.time()
        
        with gzip.open(vcf_file, 'rt') as f:
            for line_num, line in enumerate(f, 1):
                # Skip headers
                if line.startswith('#'):
                    continue
                
                # Process variant
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    
                    try:
                        pos = int(parts[1])
                        qual = float(parts[5]) if parts[5] != '.' else 0.0
                    except:
                        continue
                    
                    rsid = parts[2]
                    ref = parts[3]
                    alt = parts[4]
                    filter_val = parts[6]
                    info = parts[7]
                    
                    # Extract allele frequency and other info
                    allele_freq = 0.0
                    variant_class = "unknown"
                    gene_info = "unknown"
                    
                    # Parse INFO field
                    if "AF=" in info:
                        try:
                            af_part = info.split("AF=")[1].split(";")[0]
                            allele_freq = float(af_part)
                        except:
                            pass
                    
                    if "VC=" in info:
                        try:
                            variant_class = info.split("VC=")[1].split(";")[0]
                        except:
                            pass
                    
                    if "GENEINFO=" in info:
                        try:
                            gene_info = info.split("GENEINFO=")[1].split(";")[0]
                        except:
                            pass
                    
                    variants_batch.append((
                        chrom, pos, rsid, ref, alt, qual, filter_val,
                        allele_freq, variant_class, gene_info
                    ))
                
                # Insert in batches
                if len(variants_batch) >= batch_size:
                    try:
                        client.insert('genomics_db.dbsnp_common', variants_batch)
                        total_processed += len(variants_batch)
                        
                        elapsed = time.time() - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        
                        if total_processed % 100000 == 0:
                            log(f"   Processed: {total_processed:,} variants ({rate:.0f}/sec)")
                        
                        variants_batch = []
                        
                    except Exception as e:
                        log(f"   Batch error: {e}")
                        variants_batch = []
        
        # Insert final batch
        if variants_batch:
            client.insert('genomics_db.dbsnp_common', variants_batch)
            total_processed += len(variants_batch)
        
        total_time = time.time() - start_time
        
        log(f"\nDBSNP MIGRATION COMPLETE:")
        log(f"Total variants: {total_processed:,}")
        log(f"Processing time: {total_time:.1f}s ({total_time/60:.1f} min)")
        log(f"Processing rate: {total_processed/total_time:.0f} variants/sec")
        
        # Test final performance
        log("Testing dbSNP performance...")
        
        start = time.time()
        final_count = client.query("SELECT COUNT(*) FROM genomics_db.dbsnp_common").result_rows[0][0]
        count_time = time.time() - start
        
        start = time.time()
        common_variants = client.query("SELECT COUNT(*) FROM genomics_db.dbsnp_common WHERE allele_frequency > 0.01").result_rows[0][0]
        freq_time = time.time() - start
        
        log(f"Final count: {final_count:,} in {count_time:.4f}s")
        log(f"Common variants (>1%): {common_variants:,} in {freq_time:.4f}s")
        
        if count_time < 0.1 and freq_time < 0.1:
            log("EXCELLENT: dbSNP queries <0.1s")
        
        return True
        
    except Exception as e:
        log(f"ERROR: dbSNP migration failed - {e}")
        return False

if __name__ == "__main__":
    success = migrate_dbsnp_variants()
    if success:
        print("DBSNP MIGRATION SUCCESS!")
        print("Ready for Phase 3: SpliceAI (122 GB)")
    else:
        print("DBSNP MIGRATION FAILED")
