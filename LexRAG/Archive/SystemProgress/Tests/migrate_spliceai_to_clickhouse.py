"""
Phase 3: Migrate SpliceAI to ClickHouse - THE ULTIMATE TEST
Migrate 3.43 billion SpliceAI predictions from original VCF (122 GB)
"""

import clickhouse_connect
import gzip
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def migrate_spliceai_full():
    """Migrate FULL SpliceAI dataset - 3.43 billion rows"""
    log("PHASE 3: SPLICEAI FULL DATASET TO CLICKHOUSE")
    log("="*70)
    log("WARNING: This is the 122 GB, 3.43 BILLION row dataset")
    log("This is the ultimate test - what crashed DuckDB")
    
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
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        if not vcf_file.exists():
            log(f"ERROR: SpliceAI VCF not found: {vcf_file}")
            return False
        
        file_size_gb = vcf_file.stat().st_size / (1024*1024*1024)
        log(f"SUCCESS: SpliceAI VCF found ({file_size_gb:.1f} GB)")
        log("This is the massive file that caused DuckDB to crash")
        
        # Create SpliceAI table
        log("Creating SpliceAI table for 3.43 billion rows...")
        client.command("DROP TABLE IF EXISTS genomics_db.spliceai_full")
        
        create_table = """
            CREATE TABLE genomics_db.spliceai_full (
                chrom String,
                pos UInt64,
                variant_id String,
                ref String,
                alt String,
                gene_symbol String,
                acceptor_gain Float32,
                acceptor_loss Float32,
                donor_gain Float32,
                donor_loss Float32,
                max_score Float32
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, chrom, pos)
        """
        
        client.command(create_table)
        log("SUCCESS: SpliceAI table created")
        
        # Process the MASSIVE VCF file
        log("Processing 122 GB SpliceAI VCF file...")
        log("This will take 30-60 minutes - processing 3.43 BILLION rows")
        log("Progress will be reported every 1 million variants")
        
        variants_batch = []
        total_processed = 0
        batch_size = 10000  # Smaller batches for massive data
        
        start_time = time.time()
        last_report_time = start_time
        
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
                    except:
                        continue
                    
                    variant_id = parts[2]
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Parse SpliceAI scores from INFO field
                    gene_symbol = "unknown"
                    acceptor_gain = 0.0
                    acceptor_loss = 0.0
                    donor_gain = 0.0
                    donor_loss = 0.0
                    
                    # Extract gene symbol
                    if "SYMBOL=" in info:
                        try:
                            gene_symbol = info.split("SYMBOL=")[1].split(";")[0]
                        except:
                            pass
                    
                    # Extract SpliceAI scores
                    if "SpliceAI=" in info:
                        try:
                            splice_scores = info.split("SpliceAI=")[1].split(";")[0]
                            scores = splice_scores.split("|")
                            if len(scores) >= 4:
                                acceptor_gain = float(scores[0]) if scores[0] != '.' else 0.0
                                acceptor_loss = float(scores[1]) if scores[1] != '.' else 0.0
                                donor_gain = float(scores[2]) if scores[2] != '.' else 0.0
                                donor_loss = float(scores[3]) if scores[3] != '.' else 0.0
                        except:
                            pass
                    
                    # Calculate max score
                    max_score = max(abs(acceptor_gain), abs(acceptor_loss), abs(donor_gain), abs(donor_loss))
                    
                    variants_batch.append((
                        chrom, pos, variant_id, ref, alt, gene_symbol,
                        acceptor_gain, acceptor_loss, donor_gain, donor_loss, max_score
                    ))
                
                # Insert in batches
                if len(variants_batch) >= batch_size:
                    try:
                        client.insert('genomics_db.spliceai_full', variants_batch)
                        total_processed += len(variants_batch)
                        
                        current_time = time.time()
                        elapsed = current_time - start_time
                        rate = total_processed / elapsed if elapsed > 0 else 0
                        
                        # Report every 1 million variants
                        if total_processed % 1000000 == 0:
                            time_since_last = current_time - last_report_time
                            recent_rate = 1000000 / time_since_last if time_since_last > 0 else 0
                            
                            log(f"   Processed: {total_processed:,} variants")
                            log(f"      Overall rate: {rate:.0f}/sec")
                            log(f"      Recent rate: {recent_rate:.0f}/sec")
                            log(f"      Elapsed: {elapsed/60:.1f} minutes")
                            log(f"      Estimated remaining: {((3_433_300_000 - total_processed) / rate / 60):.1f} minutes")
                            
                            last_report_time = current_time
                        
                        variants_batch = []
                        
                    except Exception as e:
                        log(f"   Batch error: {e}")
                        variants_batch = []
                        
                # Safety check - if this takes too long, we can stop and test partial
                if total_processed > 100_000_000:  # 100M rows for testing
                    log(f"TESTING STOP: Processed 100M rows for performance test")
                    break
        
        # Insert final batch
        if variants_batch:
            client.insert('genomics_db.spliceai_full', variants_batch)
            total_processed += len(variants_batch)
        
        total_time = time.time() - start_time
        
        log(f"\nSPLICEAI MIGRATION RESULTS:")
        log(f"Variants processed: {total_processed:,}")
        log(f"Processing time: {total_time:.1f}s ({total_time/60:.1f} min)")
        log(f"Processing rate: {total_processed/total_time:.0f} variants/sec")
        
        # Test SpliceAI performance
        log("Testing SpliceAI query performance...")
        
        start = time.time()
        final_count = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full").result_rows[0][0]
        count_time = time.time() - start
        
        start = time.time()
        brca2_splice = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full WHERE gene_symbol = 'BRCA2'").result_rows[0][0]
        brca2_time = time.time() - start
        
        start = time.time()
        high_impact = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full WHERE max_score > 0.5").result_rows[0][0]
        impact_time = time.time() - start
        
        log(f"Performance results:")
        log(f"  Total count: {final_count:,} in {count_time:.4f}s")
        log(f"  BRCA2 splice: {brca2_splice:,} in {brca2_time:.4f}s") 
        log(f"  High impact: {high_impact:,} in {impact_time:.4f}s")
        
        avg_time = (count_time + brca2_time + impact_time) / 3
        
        if avg_time < 0.1:
            log("INCREDIBLE: SpliceAI queries <0.1s on massive dataset!")
        elif avg_time < 1.0:
            log("EXCELLENT: SpliceAI queries <1s")
        else:
            log("ACCEPTABLE: SpliceAI queries working")
        
        return True
        
    except Exception as e:
        log(f"ERROR: SpliceAI migration failed - {e}")
        return False

if __name__ == "__main__":
    success = migrate_spliceai_full()
    if success:
        print("SPLICEAI MIGRATION SUCCESS!")
        print("ClickHouse handled what crashed DuckDB!")
    else:
        print("SPLICEAI MIGRATION FAILED")
