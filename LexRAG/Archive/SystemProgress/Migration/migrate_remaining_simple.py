"""
Simple Remaining Dataset Migration using subprocess calls to clickhouse-client
This version works by calling the clickhouse-client directly instead of using the Python library
"""

import subprocess
import gzip
import time
import os
import gc
import psutil
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def log_system_status():
    """Log current system resource usage"""
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        log(f"💻 SYSTEM STATUS:")
        log(f"   Memory: {memory.percent:.1f}% used ({memory.available/(1024**3):.1f}GB available)")
        log(f"   CPU: {cpu:.1f}% usage")
        
        if memory.percent > 85:
            log(f"⚠️  WARNING: Memory usage high ({memory.percent:.1f}%)")
    except Exception as e:
        log(f"⚠️  Could not get system status: {e}")

def clickhouse_query(query, return_output=False):
    """Execute ClickHouse query via docker exec"""
    try:
        cmd = f'docker exec clickhouse-genomics clickhouse-client --query "{query}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            log(f"❌ Query failed: {result.stderr}")
            return None
        
        if return_output:
            return result.stdout.strip()
        return True
        
    except subprocess.TimeoutExpired:
        log("⚠️  Query timed out")
        return None
    except Exception as e:
        log(f"❌ Query error: {e}")
        return None

def setup_tables():
    """Create missing tables"""
    log("SETTING UP MISSING TABLES")
    log("="*60)
    
    # SpliceAI table (recreate after corruption)
    log("🧬 Creating SpliceAI table...")
    query = """
    DROP TABLE IF EXISTS genomics_db.spliceai_predictions;
    CREATE TABLE genomics_db.spliceai_predictions (
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
    ORDER BY (gene_symbol, chrom, pos);
    """
    
    if clickhouse_query(query):
        log("✅ SpliceAI table created")
    else:
        log("❌ Failed to create SpliceAI table")
        return False
    
    return True

def migrate_spliceai_safe():
    """Migrate SpliceAI with very small batches and monitoring"""
    log("\n🚀 MIGRATING SPLICEAI PREDICTIONS (ULTRA-SAFE MODE)")
    log("="*60)
    log("⚠️  Using tiny batches and frequent monitoring")
    
    vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
    if not vcf_file.exists():
        log(f"❌ SpliceAI VCF not found: {vcf_file}")
        return False
    
    file_size_gb = vcf_file.stat().st_size / (1024*1024*1024)
    log(f"📁 Processing: {vcf_file.name} ({file_size_gb:.1f} GB)")
    
    # Create temporary CSV file for batch inserts
    temp_csv = Path("temp_spliceai_batch.csv")
    
    total = 0
    batch_size = 1000  # Very small batches
    progress_interval = 10000  # Report every 10K
    memory_check_interval = 50000  # Check memory every 50K
    start_time = time.time()
    
    try:
        with gzip.open(vcf_file, 'rt') as f:
            batch_lines = []
            
            for line_num, line in enumerate(f, 1):
                if line.startswith('#'):
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    try:
                        pos = int(parts[1])
                    except:
                        continue
                    
                    variant_id = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Parse SpliceAI scores
                    gene_symbol = "unknown"
                    acceptor_gain = 0.0
                    acceptor_loss = 0.0
                    donor_gain = 0.0
                    donor_loss = 0.0
                    
                    if "SYMBOL=" in info:
                        try:
                            gene_symbol = info.split("SYMBOL=")[1].split(";")[0]
                        except:
                            pass
                    
                    if "SpliceAI=" in info:
                        try:
                            scores = info.split("SpliceAI=")[1].split(";")[0].split("|")
                            if len(scores) >= 4:
                                acceptor_gain = float(scores[0]) if scores[0] != '.' else 0.0
                                acceptor_loss = float(scores[1]) if scores[1] != '.' else 0.0
                                donor_gain = float(scores[2]) if scores[2] != '.' else 0.0
                                donor_loss = float(scores[3]) if scores[3] != '.' else 0.0
                        except:
                            pass
                    
                    max_score = max(abs(acceptor_gain), abs(acceptor_loss), abs(donor_gain), abs(donor_loss))
                    
                    # Create CSV line
                    csv_line = f"{chrom}\t{pos}\t{variant_id}\t{ref}\t{alt}\t{gene_symbol}\t{acceptor_gain}\t{acceptor_loss}\t{donor_gain}\t{donor_loss}\t{max_score}"
                    batch_lines.append(csv_line)
                
                # Process in very small batches
                if len(batch_lines) >= batch_size:
                    try:
                        # Write batch to temp file
                        with open(temp_csv, 'w') as csv_file:
                            csv_file.write('\n'.join(batch_lines))
                        
                        # Insert via clickhouse-client
                        insert_cmd = f"cat {temp_csv} | docker exec -i clickhouse-genomics clickhouse-client --query \"INSERT INTO genomics_db.spliceai_predictions FORMAT TabSeparated\""
                        result = subprocess.run(insert_cmd, shell=True, capture_output=True)
                        
                        if result.returncode == 0:
                            total += len(batch_lines)
                            
                            # Progress reporting
                            if total % progress_interval == 0:
                                elapsed = time.time() - start_time
                                rate = total / elapsed if elapsed > 0 else 0
                                remaining = 3_433_300_000 - total
                                eta_hours = remaining / rate / 3600 if rate > 0 else 0
                                
                                log(f"📊 SpliceAI Progress:")
                                log(f"   ✅ Processed: {total:,} variants ({total/3_433_300_000*100:.4f}% complete)")
                                log(f"   ⚡ Speed: {rate:.0f} variants/sec")
                                log(f"   ⏰ ETA: {eta_hours:.1f} hours remaining")
                                log(f"   📈 Current gene: {gene_symbol}")
                            
                            # System monitoring
                            if total % memory_check_interval == 0:
                                log_system_status()
                                gc.collect()
                                time.sleep(1)  # Brief pause
                        else:
                            log(f"⚠️  Batch insert failed: {result.stderr.decode()}")
                        
                        batch_lines = []
                        
                    except Exception as e:
                        log(f"⚠️  Batch processing error: {e}")
                        batch_lines = []
                
                # Safety check - stop if we've processed a reasonable amount for testing
                if total >= 1_000_000:  # Stop after 1M records for initial test
                    log(f"🛑 Stopping after {total:,} records for initial test")
                    break
        
        # Process final batch
        if batch_lines:
            try:
                with open(temp_csv, 'w') as csv_file:
                    csv_file.write('\n'.join(batch_lines))
                
                insert_cmd = f"cat {temp_csv} | docker exec -i clickhouse-genomics clickhouse-client --query \"INSERT INTO genomics_db.spliceai_predictions FORMAT TabSeparated\""
                result = subprocess.run(insert_cmd, shell=True, capture_output=True)
                
                if result.returncode == 0:
                    total += len(batch_lines)
            except Exception as e:
                log(f"⚠️  Final batch error: {e}")
        
        # Cleanup
        if temp_csv.exists():
            temp_csv.unlink()
        
        elapsed = time.time() - start_time
        log(f"✅ SpliceAI test complete: {total:,} variants in {elapsed/60:.1f} minutes")
        return total > 100000  # Success if we got >100K records
        
    except Exception as e:
        log(f"❌ SpliceAI migration failed: {e}")
        if temp_csv.exists():
            temp_csv.unlink()
        return False

def main():
    log("="*80)
    log("🚀 STARTING SPLICEAI TEST MIGRATION")
    log("="*80)
    log("This will test SpliceAI migration with first 1M records")
    log("="*80)
    
    # Initial system check
    log("🔍 INITIAL SYSTEM CHECK:")
    log_system_status()
    
    # Test ClickHouse connection
    log("🔌 Testing ClickHouse connection...")
    test_result = clickhouse_query("SELECT COUNT(*) FROM genomics_db.clinvar_variants", return_output=True)
    if test_result:
        log(f"✅ ClickHouse connected - ClinVar has {test_result} variants")
    else:
        log("❌ ClickHouse connection failed")
        return
    
    # Setup tables
    if not setup_tables():
        log("❌ Table setup failed")
        return
    
    # Run SpliceAI test migration
    log("\n" + "="*80)
    success = migrate_spliceai_safe()
    
    if success:
        log("🎉 SPLICEAI TEST MIGRATION SUCCESSFUL!")
        log("Ready to run full migration")
    else:
        log("❌ SpliceAI test migration failed")

if __name__ == "__main__":
    main()
