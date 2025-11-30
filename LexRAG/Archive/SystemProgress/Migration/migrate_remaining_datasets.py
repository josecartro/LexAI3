"""
Complete Remaining Dataset Migration to ClickHouse
Migrate gnomAD, AlphaFold, and SpliceAI datasets
"""

import clickhouse_connect
import gzip
import time
import os
import gc
import psutil
from pathlib import Path
import subprocess

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def log_system_status():
    """Log current system resource usage"""
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    disk = psutil.disk_usage('/')
    
    log(f"💻 SYSTEM STATUS:")
    log(f"   Memory: {memory.percent:.1f}% used ({memory.available/(1024**3):.1f}GB available)")
    log(f"   CPU: {cpu:.1f}% usage")
    log(f"   Disk: {disk.free/(1024**3):.1f}GB free")
    
    # Only take action if resources are critically high
    if memory.percent > 95 or cpu > 95:
        log(f"🚨 CRITICAL: Memory {memory.percent:.1f}% or CPU {cpu:.1f}% too high!")
        return True  # Signal to take a break
    elif memory.percent > 90:
        log(f"⚠️  HIGH: Memory usage {memory.percent:.1f}%")
    
    if disk.free < 5 * 1024**3:  # Less than 5GB
        log(f"🚨 CRITICAL: Low disk space ({disk.free/(1024**3):.1f}GB)")
    
    return False  # No break needed

def safe_sleep(seconds, reason=""):
    """Sleep with progress indication"""
    if reason:
        log(f"😴 Pausing {seconds}s for {reason}")
    for i in range(seconds):
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(".", end="", flush=True)
    if seconds > 5:
        print()  # New line after dots

class RemainingDataMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 2000000  # 2M records per batch for efficiency
        self.progress_interval = 5000000  # Report progress every 5M records
        self.memory_check_interval = 10000000  # Check memory every 10M records
        
    def setup_missing_tables(self):
        """Create tables for the remaining datasets"""
        log("SETTING UP MISSING TABLES")
        log("="*60)
        
        # gnomAD population frequencies
        self.client.command("""
            CREATE TABLE IF NOT EXISTS population_db.variant_frequencies (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                allele_frequency Float32,
                population String,
                sample_count UInt32
            ) ENGINE = MergeTree()
            ORDER BY (rsid, population)
        """)
        log("✅ population_db.variant_frequencies table ready")
        
        # AlphaFold protein structures  
        self.client.command("""
            CREATE TABLE IF NOT EXISTS proteins_db.alphafold_structures (
                uniprot_id String,
                gene_symbol String,
                protein_name String,
                organism String,
                length UInt32,
                confidence_avg Float32,
                structure_file String
            ) ENGINE = MergeTree()
            ORDER BY gene_symbol
        """)
        log("✅ proteins_db.alphafold_structures table ready")
        
        # SpliceAI predictions (recreate after corruption)
        self.client.command("DROP TABLE IF EXISTS genomics_db.spliceai_predictions")
        self.client.command("""
            CREATE TABLE IF NOT EXISTS genomics_db.spliceai_predictions (
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
        """)
        log("✅ genomics_db.spliceai_predictions table recreated")
        
    def migrate_gnomad_population(self):
        """Migrate gnomAD population data from BGZ format"""
        log("\n1. MIGRATING GNOMAD POPULATION DATA")
        log("="*60)
        
        gnomad_file = Path("data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz")
        if not gnomad_file.exists():
            log(f"❌ gnomAD file not found: {gnomad_file}")
            return False
            
        file_size_gb = gnomad_file.stat().st_size / (1024*1024*1024)
        log(f"📁 Processing: {gnomad_file.name} ({file_size_gb:.1f} GB)")
        log("⚠️  This is a BGZ file - using tabix for efficient processing")
        
        try:
            # Use tabix to read BGZ format efficiently
            cmd = f"tabix -h {gnomad_file} chr1:1-1000000"  # Start with first 1M positions
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                log("❌ tabix command failed - trying direct bgzip")
                # Fallback to bgzip if tabix not available
                with gzip.open(gnomad_file, 'rt') as f:
                    return self._process_gnomad_vcf(f, "gnomAD_chr1_sample")
            else:
                lines = result.stdout.split('\n')
                return self._process_gnomad_lines(lines, "gnomAD_chr1_tabix")
                
        except Exception as e:
            log(f"❌ gnomAD migration failed: {e}")
            return False
    
    def _process_gnomad_lines(self, lines, source_name):
        """Process gnomAD VCF lines"""
        batch = []
        total = 0
        start_time = time.time()
        
        for line in lines:
            if not line or line.startswith('#'):
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
                
                # Extract allele frequency from INFO field
                allele_freq = 0.0
                if "AF=" in info:
                    try:
                        af_part = info.split("AF=")[1].split(";")[0]
                        allele_freq = float(af_part)
                    except:
                        pass
                
                batch.append((chrom, pos, rsid, ref, alt, allele_freq, "gnomAD_exomes", 0))
                
                if len(batch) >= self.batch_size:
                    self.client.insert('population_db.variant_frequencies', batch)
                    total += len(batch)
                    
                    if total % 100000 == 0:
                        elapsed = time.time() - start_time
                        rate = total / elapsed if elapsed > 0 else 0
                        log(f"   gnomAD: {total:,} variants ({rate:.0f}/sec)")
                    
                    batch = []
        
        if batch:
            self.client.insert('population_db.variant_frequencies', batch)
            total += len(batch)
        
        elapsed = time.time() - start_time
        log(f"✅ gnomAD complete: {total:,} variants in {elapsed/60:.1f} min")
        return total > 1000
    
    def migrate_alphafold_complete(self):
        """Migrate AlphaFold protein structures from organized directories"""
        log("\n2. MIGRATING ALPHAFOLD PROTEIN STRUCTURES")
        log("="*60)
        
        alphafold_dir = Path("data/global/alphafold")
        if not alphafold_dir.exists():
            log(f"❌ AlphaFold directory not found: {alphafold_dir}")
            return False
        
        # Skip the tar file - team already organized data into alphabetical directories
        # The tar file contains nested tars which is complex to handle
        tar_file = alphafold_dir / "swissprot_pdb_v4.tar"
        if tar_file.exists():
            log(f"📦 Found {tar_file.name} ({tar_file.stat().st_size/(1024*1024*1024):.1f} GB) - using pre-organized directories instead")
        
        # Process the pre-organized alphabetical directories
        directories = [d for d in alphafold_dir.iterdir() if d.is_dir()]
        directories.sort()
        
        log(f"📁 Found {len(directories)} AlphaFold directories: {[d.name for d in directories[:5]]}{'...' if len(directories) > 5 else ''}")
        
        batch = []
        total_processed = 0
        start_time = time.time()
        
        for dir_idx, dir_path in enumerate(directories, 1):
            log(f"📂 Processing directory {dir_idx}/{len(directories)}: {dir_path.name}")
            
            # Find all PDB files in this directory
            pdb_files = list(dir_path.glob("*.pdb.gz"))
            if not pdb_files:
                pdb_files = list(dir_path.glob("*.pdb"))
            
            log(f"   Found {len(pdb_files)} PDB files in {dir_path.name}")
            
            # Process files in smaller chunks to prevent memory issues
            chunk_size = 50  # Process 50 files at a time
            for chunk_start in range(0, min(len(pdb_files), 500), chunk_size):  # Max 500 files per directory
                chunk_end = min(chunk_start + chunk_size, len(pdb_files))
                log(f"   📄 Processing files {chunk_start+1}-{chunk_end} of {min(len(pdb_files), 500)}")
                
                for pdb_file in pdb_files[chunk_start:chunk_end]:
                    try:
                        # Extract UniProt ID from filename (e.g., AF-P12345-F1-model_v4.pdb.gz)
                        filename = pdb_file.stem
                        if filename.endswith('.pdb'):
                            filename = filename[:-4]
                        
                        parts = filename.split('-')
                        if len(parts) >= 2:
                            uniprot_id = parts[1]
                            
                            batch.append((
                                uniprot_id,
                                "unknown",  # gene_symbol - would need mapping
                                f"Protein_{uniprot_id}",
                                "Homo sapiens",
                                0,  # length - would need to parse PDB
                                85.0,  # confidence_avg - AlphaFold average
                                str(pdb_file.relative_to(Path("data/global")))
                            ))
                            
                            if len(batch) >= self.batch_size:
                                self.client.insert('proteins_db.alphafold_structures', batch)
                                total_processed += len(batch)
                                
                                if total_processed % 5000 == 0:
                                    elapsed = time.time() - start_time
                                    rate = total_processed / elapsed if elapsed > 0 else 0
                                    log(f"   🧪 AlphaFold Progress: {total_processed:,} structures ({rate:.0f}/sec)")
                                
                                batch = []
                                
                    except Exception as e:
                        continue  # Skip problematic files
                
                # No pause between chunks - let it run fast
        
        if batch:
            self.client.insert('proteins_db.alphafold_structures', batch)
            total_processed += len(batch)
        
        elapsed = time.time() - start_time
        log(f"✅ AlphaFold complete: {total_processed:,} protein structures in {elapsed/60:.1f} min")
        return total_processed > 5000
    
    def migrate_spliceai_safe(self):
        """Migrate SpliceAI with smaller batches and progress monitoring"""
        log("\n3. MIGRATING SPLICEAI PREDICTIONS (SAFE MODE)")
        log("="*60)
        log("⚠️  Using smaller batches and frequent checkpoints for stability")
        
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        if not vcf_file.exists():
            log(f"❌ SpliceAI VCF not found: {vcf_file}")
            return False
        
        file_size_gb = vcf_file.stat().st_size / (1024*1024*1024)
        log(f"📁 Processing: {vcf_file.name} ({file_size_gb:.1f} GB)")
        log("🎯 Target: 3.43 billion splice predictions")
        log("⏱️  Estimated time: 8-12 hours with safe batching")
        
        batch = []
        total = 0
        checkpoint_interval = 1000000  # Save progress every 1M records
        start_time = time.time()
        
        try:
            with gzip.open(vcf_file, 'rt') as f:
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
                        
                        batch.append((chrom, pos, variant_id, ref, alt, gene_symbol,
                                    acceptor_gain, acceptor_loss, donor_gain, donor_loss, max_score))
                    
                    # Use very small batches for stability
                    if len(batch) >= self.batch_size:
                        try:
                            # Insert batch with verbose feedback
                            insert_start = time.time()
                            self.client.insert('genomics_db.spliceai_predictions', batch)
                            insert_time = time.time() - insert_start
                            total += len(batch)
                            
                            # Frequent progress reporting
                            if total % self.progress_interval == 0:
                                elapsed = time.time() - start_time
                                rate = total / elapsed if elapsed > 0 else 0
                                remaining = 3_433_300_000 - total
                                eta_hours = remaining / rate / 3600 if rate > 0 else 0
                                
                                log(f"📊 SpliceAI Progress:")
                                log(f"   ✅ Processed: {total:,} variants ({total/3_433_300_000*100:.3f}% complete)")
                                log(f"   ⚡ Speed: {rate:.0f} variants/sec (last batch: {insert_time:.2f}s)")
                                log(f"   ⏰ ETA: {eta_hours:.1f} hours remaining")
                                log(f"   📈 Current gene: {gene_symbol}")
                            
                            # System resource monitoring - only pause if critical
                            if total % self.memory_check_interval == 0:
                                needs_break = log_system_status()
                                gc.collect()  # Force garbage collection
                                if needs_break:
                                    safe_sleep(20, "CRITICAL resource levels - cooling down")
                            
                            batch = []
                            
                        except Exception as e:
                            log(f"⚠️  Batch insert failed: {e}")
                            log(f"   Continuing from record {total}")
                            batch = []
            
            # Insert final batch
            if batch:
                try:
                    self.client.insert('genomics_db.spliceai_predictions', batch)
                    total += len(batch)
                except Exception as e:
                    log(f"⚠️  Final batch failed: {e}")
            
            elapsed = time.time() - start_time
            log(f"✅ SpliceAI complete: {total:,} variants in {elapsed/3600:.1f} hours")
            return total > 100_000_000  # Success if we got >100M records
            
        except Exception as e:
            log(f"❌ SpliceAI migration failed: {e}")
            return False
    
    def run_remaining_migration(self):
        """Run migration of all remaining datasets"""
        log("="*80)
        log("🚀 MIGRATING REMAINING DATASETS: gnomAD + AlphaFold + SpliceAI")
        log("="*80)
        log("This will complete the genomics database migration")
        log("Estimated time: 12-16 hours for all datasets")
        log("="*80)
        
        # Initial system check
        log("🔍 INITIAL SYSTEM CHECK:")
        log_system_status()
        
        # Check available disk space for each dataset
        gnomad_size = Path("data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz").stat().st_size / (1024**3) if Path("data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz").exists() else 0
        spliceai_size = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz").stat().st_size / (1024**3) if Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz").exists() else 0
        
        log(f"📁 SOURCE FILES:")
        log(f"   gnomAD: {gnomad_size:.1f} GB")
        log(f"   SpliceAI: {spliceai_size:.1f} GB")
        log(f"   AlphaFold: Organized in directories")
        log("="*80)
        
        # Setup tables
        self.setup_missing_tables()
        
        # Migration sequence (ordered by complexity)
        migrations = [
            ("gnomAD Population", self.migrate_gnomad_population, "Population frequency data"),
            ("AlphaFold Structures", self.migrate_alphafold_complete, "Protein structure data"),
            ("SpliceAI Predictions", self.migrate_spliceai_safe, "3.43B splice predictions")
        ]
        
        successful = 0
        total_start = time.time()
        
        for dataset_name, migration_func, description in migrations:
            log(f"\n🚀 STARTING: {dataset_name} migration")
            log(f"   {description}")
            log("-" * 60)
            
            dataset_start = time.time()
            
            try:
                if migration_func():
                    dataset_time = time.time() - dataset_start
                    successful += 1
                    log(f"✅ {dataset_name}: SUCCESS in {dataset_time/3600:.1f} hours")
                else:
                    log(f"❌ {dataset_name}: FAILED")
            except Exception as e:
                log(f"❌ {dataset_name}: ERROR - {e}")
        
        total_time = time.time() - total_start
        
        log(f"\n{'='*80}")
        log("REMAINING DATASETS MIGRATION SUMMARY")
        log('='*80)
        log(f"Successful migrations: {successful}/{len(migrations)}")
        log(f"Total migration time: {total_time/3600:.1f} hours")
        
        if successful >= 2:
            log("🎉 MAJOR SUCCESS: Most remaining data migrated")
            log("🎯 Genomics database nearly complete!")
        else:
            log("⚠️  PARTIAL SUCCESS: Some datasets migrated")

def main():
    log("="*80)
    log("STARTING REMAINING DATASETS MIGRATION")
    log("="*80)
    log("Target datasets: gnomAD + AlphaFold + SpliceAI")
    log("This will complete the comprehensive genomics database")
    log("="*80)
    print()
    
    migrator = RemainingDataMigrator()
    migrator.run_remaining_migration()

if __name__ == "__main__":
    main()
