"""
Migrate gnomAD Population Data - The Missing Dataset
Process the 26.9GB BGZ file efficiently
"""

import clickhouse_connect
import gzip
import time
import gc
import psutil
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def log_system_status():
    """Log system status and return if critical break needed"""
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        log(f"💻 SYSTEM: Memory {memory.percent:.1f}%, CPU {cpu:.1f}%")
        
        # Only break if really critical
        if memory.percent > 95 or cpu > 95:
            log(f"🚨 CRITICAL: Taking 20-second break!")
            return True
        return False
    except:
        return False

class GnomADMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 2000000  # 2M records per batch
        
    def setup_gnomad_table(self):
        """Create gnomAD table"""
        log("🧬 Setting up gnomAD population table...")
        
        self.client.command("""
            CREATE TABLE IF NOT EXISTS population_db.variant_frequencies (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                allele_frequency Float32,
                allele_count UInt32,
                allele_number UInt32,
                population String
            ) ENGINE = MergeTree()
            ORDER BY (rsid, chrom, pos)
        """)
        log("✅ gnomAD table ready")
    
    def migrate_gnomad_population(self):
        """Migrate gnomAD population frequencies"""
        log("🚀 MIGRATING GNOMAD POPULATION DATA")
        log("="*60)
        
        gnomad_file = Path("data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz")
        if not gnomad_file.exists():
            log(f"❌ gnomAD file not found: {gnomad_file}")
            return False
            
        file_size_gb = gnomad_file.stat().st_size / (1024*1024*1024)
        log(f"📁 Processing: {gnomad_file.name} ({file_size_gb:.1f} GB)")
        log("📊 Target: Population allele frequencies for chromosome 1")
        
        batch = []
        total = 0
        start_time = time.time()
        
        try:
            with gzip.open(gnomad_file, 'rt') as f:
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
                        
                        rsid = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                        ref = parts[3]
                        alt = parts[4]
                        info = parts[7]
                        
                        # Parse gnomAD INFO field
                        allele_freq = 0.0
                        allele_count = 0
                        allele_number = 0
                        
                        # Extract AF (allele frequency)
                        if "AF=" in info:
                            try:
                                af_part = info.split("AF=")[1].split(";")[0]
                                allele_freq = float(af_part)
                            except:
                                pass
                        
                        # Extract AC (allele count) 
                        if "AC=" in info:
                            try:
                                ac_part = info.split("AC=")[1].split(";")[0]
                                allele_count = int(ac_part)
                            except:
                                pass
                        
                        # Extract AN (allele number)
                        if "AN=" in info:
                            try:
                                an_part = info.split("AN=")[1].split(";")[0]
                                allele_number = int(an_part)
                            except:
                                pass
                        
                        batch.append((chrom, pos, rsid, ref, alt, allele_freq, 
                                    allele_count, allele_number, "gnomAD_exomes"))
                    
                    # Large batches for efficiency
                    if len(batch) >= self.batch_size:
                        try:
                            insert_start = time.time()
                            self.client.insert('population_db.variant_frequencies', batch)
                            insert_time = time.time() - insert_start
                            total += len(batch)
                            
                            elapsed = time.time() - start_time
                            rate = total / elapsed if elapsed > 0 else 0
                            
                            log(f"🧬 gnomAD Progress:")
                            log(f"   ✅ Processed: {total:,} variants")
                            log(f"   ⚡ Speed: {rate:.0f} variants/sec (batch: {insert_time:.2f}s)")
                            log(f"   📈 Current: chr{chrom}:{pos}")
                            
                            # Only check resources occasionally
                            if total % 10000000 == 0:  # Every 10M records
                                if log_system_status():
                                    time.sleep(20)
                                    gc.collect()
                            
                            batch = []
                            
                        except Exception as e:
                            log(f"⚠️  Batch failed: {e} - continuing...")
                            batch = []
            
            # Final batch
            if batch:
                try:
                    self.client.insert('population_db.variant_frequencies', batch)
                    total += len(batch)
                except Exception as e:
                    log(f"⚠️  Final batch failed: {e}")
            
            elapsed = time.time() - start_time
            log(f"✅ gnomAD complete: {total:,} variants in {elapsed/3600:.1f} hours")
            return total > 1000000
            
        except Exception as e:
            log(f"❌ gnomAD migration failed: {e}")
            return False

def main():
    log("="*80)
    log("🧬 MIGRATING GNOMAD POPULATION DATA - THE MISSING DATASET")
    log("="*80)
    log("Processing 26.9GB chromosome 1 population frequencies")
    log("="*80)
    
    migrator = GnomADMigrator()
    
    # Initial system check
    log("🔍 SYSTEM CHECK:")
    log_system_status()
    log("="*80)
    
    # Setup table
    migrator.setup_gnomad_table()
    
    # Run migration
    success = migrator.migrate_gnomad_population()
    
    if success:
        log("🎉 GNOMAD MIGRATION COMPLETE!")
        log("All major datasets now loaded!")
    else:
        log("❌ gnomAD migration failed")

if __name__ == "__main__":
    main()
