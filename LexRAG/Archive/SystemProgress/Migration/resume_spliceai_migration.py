"""
Resume SpliceAI Migration from where it left off
Much faster settings - no unnecessary pauses
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
        cpu = psutil.cpu_percent(interval=0.1)  # Quick check
        
        # Only log every few checks to reduce spam
        if hasattr(log_system_status, 'check_count'):
            log_system_status.check_count += 1
        else:
            log_system_status.check_count = 1
        
        if log_system_status.check_count % 5 == 0:  # Log every 5th check
            log(f"💻 SYSTEM: Memory {memory.percent:.1f}%, CPU {cpu:.1f}%")
        
        # Only break if REALLY critical
        if memory.percent > 95 or cpu > 95:
            log(f"🚨 CRITICAL: Memory {memory.percent:.1f}% or CPU {cpu:.1f}% - taking break!")
            return True
        
        return False
    except:
        return False

class FastSpliceAIMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 5000000  # 5M records per batch - much faster
        
    def get_current_count(self):
        """Get current number of records to resume from"""
        try:
            count = self.client.query("SELECT COUNT(*) FROM genomics_db.spliceai_predictions").result_rows[0][0]
            return count
        except:
            return 0
    
    def resume_spliceai_migration(self):
        """Resume SpliceAI migration from current position"""
        log("🚀 RESUMING SPLICEAI MIGRATION - FAST MODE")
        log("="*60)
        
        # Check current progress
        current_count = self.get_current_count()
        log(f"📊 Current progress: {current_count:,} variants already loaded")
        
        if current_count > 0:
            log(f"✅ Resuming from {current_count:,} records")
            percentage = current_count / 3_433_300_000 * 100
            log(f"   Already {percentage:.2f}% complete")
        
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        if not vcf_file.exists():
            log(f"❌ SpliceAI VCF not found: {vcf_file}")
            return False
        
        file_size_gb = vcf_file.stat().st_size / (1024*1024*1024)
        log(f"📁 Processing: {vcf_file.name} ({file_size_gb:.1f} GB)")
        
        batch = []
        total_processed = 0  # New records processed this session
        lines_read = 0
        skip_count = current_count  # Skip already processed records
        start_time = time.time()
        
        log(f"⏭️  Skipping first {skip_count:,} records...")
        
        try:
            with gzip.open(vcf_file, 'rt') as f:
                for line_num, line in enumerate(f, 1):
                    if line.startswith('#'):
                        continue
                    
                    lines_read += 1
                    
                    # Skip records we already processed
                    if lines_read <= skip_count:
                        if lines_read % 10000000 == 0:  # Progress while skipping
                            log(f"   Skipping: {lines_read:,} / {skip_count:,}")
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
                        
                        batch.append((chrom, pos, variant_id, ref, alt, gene_symbol,
                                    acceptor_gain, acceptor_loss, donor_gain, donor_loss, max_score))
                    
                    # Large batches for speed
                    if len(batch) >= self.batch_size:
                        try:
                            insert_start = time.time()
                            self.client.insert('genomics_db.spliceai_predictions', batch)
                            insert_time = time.time() - insert_start
                            total_processed += len(batch)
                            total_records = current_count + total_processed
                            
                            elapsed = time.time() - start_time
                            rate = total_processed / elapsed if elapsed > 0 else 0
                            remaining = 3_433_300_000 - total_records
                            eta_hours = remaining / rate / 3600 if rate > 0 else 0
                            
                            log(f"🚀 FAST PROGRESS:")
                            log(f"   ✅ Total: {total_records:,} variants ({total_records/3_433_300_000*100:.3f}% complete)")
                            log(f"   ⚡ Speed: {rate:.0f} variants/sec (batch: {insert_time:.2f}s)")
                            log(f"   ⏰ ETA: {eta_hours:.1f} hours ({eta_hours*60:.0f} minutes)")
                            log(f"   📈 Gene: {gene_symbol}")
                            
                            # Only check resources occasionally and only break if critical
                            if total_processed % 50000000 == 0:  # Every 50M new records
                                if log_system_status():
                                    log("⏸️  Taking 20-second break for critical resources...")
                                    time.sleep(20)
                                    gc.collect()
                            
                            batch = []
                            
                        except Exception as e:
                            log(f"⚠️  Batch failed: {e} - continuing...")
                            batch = []
        
            # Final batch
            if batch:
                try:
                    self.client.insert('genomics_db.spliceai_predictions', batch)
                    total_processed += len(batch)
                except Exception as e:
                    log(f"⚠️  Final batch failed: {e}")
            
            elapsed = time.time() - start_time
            final_count = self.get_current_count()
            
            log(f"✅ SESSION COMPLETE:")
            log(f"   New records: {total_processed:,} in {elapsed/3600:.1f} hours")
            log(f"   Total records: {final_count:,}")
            log(f"   Overall progress: {final_count/3_433_300_000*100:.3f}%")
            
            return True
            
        except Exception as e:
            log(f"❌ Migration failed: {e}")
            return False

def main():
    log("="*80)
    log("🚀 RESUMING SPLICEAI MIGRATION - OPTIMIZED FOR SPEED")
    log("="*80)
    log("Settings: 5M batch size, minimal pauses, only break if CPU/Memory >95%")
    log("="*80)
    
    migrator = FastSpliceAIMigrator()
    
    # Initial system check
    log("🔍 SYSTEM CHECK:")
    log_system_status()
    log("="*80)
    
    success = migrator.resume_spliceai_migration()
    
    if success:
        log("🎉 SPLICEAI MIGRATION SESSION COMPLETE!")
    else:
        log("❌ Migration session failed")

if __name__ == "__main__":
    main()
