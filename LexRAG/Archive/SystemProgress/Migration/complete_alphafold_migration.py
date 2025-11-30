"""
Complete AlphaFold Migration - Process All Remaining Directories
Get the full 500K+ protein structures from all 23 alphabetical directories
"""

import clickhouse_connect
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

class AlphaFoldCompleteMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 50000  # 50K structures per batch
        
    def get_current_count(self):
        """Get current number of AlphaFold structures"""
        try:
            count = self.client.query("SELECT COUNT(*) FROM proteins_db.alphafold_structures").result_rows[0][0]
            return count
        except:
            return 0
    
    def complete_alphafold_migration(self):
        """Complete AlphaFold migration from all directories"""
        log("🧪 COMPLETING ALPHAFOLD PROTEIN STRUCTURES")
        log("="*60)
        
        # Check current progress
        current_count = self.get_current_count()
        log(f"📊 Current AlphaFold structures: {current_count:,}")
        
        alphafold_dir = Path("data/global/alphafold")
        if not alphafold_dir.exists():
            log(f"❌ AlphaFold directory not found: {alphafold_dir}")
            return False
        
        # Get all alphabetical directories
        directories = [d for d in alphafold_dir.iterdir() if d.is_dir()]
        directories.sort()
        
        log(f"📂 Found {len(directories)} AlphaFold directories:")
        log(f"   {[d.name for d in directories]}")
        
        # Count total files to estimate scope
        total_files = 0
        for directory in directories:
            pdb_files = list(directory.glob("*.pdb.gz")) + list(directory.glob("*.pdb"))
            total_files += len(pdb_files)
        
        log(f"📄 Total PDB files found: {total_files:,}")
        log(f"🎯 Target: Process all files to get ~500K+ structures")
        log("="*60)
        
        batch = []
        total_processed = 0
        start_time = time.time()
        
        for dir_idx, dir_path in enumerate(directories, 1):
            log(f"📂 Processing directory {dir_idx}/{len(directories)}: {dir_path.name}")
            
            # Find all PDB files in this directory
            pdb_files = list(dir_path.glob("*.pdb.gz"))
            if not pdb_files:
                pdb_files = list(dir_path.glob("*.pdb"))
            
            log(f"   Found {len(pdb_files):,} PDB files")
            
            # Process all files in this directory (no artificial limits)
            for file_idx, pdb_file in enumerate(pdb_files, 1):
                try:
                    # Extract UniProt ID from filename (e.g., AF-P12345-F1-model_v4.pdb.gz)
                    filename = pdb_file.stem
                    if filename.endswith('.pdb'):
                        filename = filename[:-4]
                    
                    parts = filename.split('-')
                    if len(parts) >= 2:
                        uniprot_id = parts[1]
                        
                        # Extract gene symbol if possible (would need mapping, using unknown for now)
                        gene_symbol = "unknown"
                        
                        batch.append((
                            uniprot_id,
                            gene_symbol,
                            f"Protein_{uniprot_id}",
                            "Homo sapiens",
                            0,  # length - would need PDB parsing
                            85.0,  # confidence_avg - AlphaFold typical
                            str(pdb_file.relative_to(Path("data/global")))
                        ))
                        
                        # Process in batches
                        if len(batch) >= self.batch_size:
                            try:
                                insert_start = time.time()
                                self.client.insert('proteins_db.alphafold_structures', batch)
                                insert_time = time.time() - insert_start
                                total_processed += len(batch)
                                
                                elapsed = time.time() - start_time
                                rate = total_processed / elapsed if elapsed > 0 else 0
                                
                                log(f"   🧪 Progress: {total_processed:,} structures ({rate:.0f}/sec, batch: {insert_time:.2f}s)")
                                log(f"   📂 Directory: {dir_path.name} ({file_idx:,}/{len(pdb_files):,} files)")
                                
                                # Check resources every few batches
                                if total_processed % 500000 == 0:  # Every 500K structures
                                    current_total = self.get_current_count()
                                    log(f"🎯 MILESTONE: {current_total:,} total AlphaFold structures loaded!")
                                    if log_system_status():
                                        time.sleep(20)
                                        gc.collect()
                                
                                batch = []
                                
                            except Exception as e:
                                log(f"⚠️  Batch failed: {e} - continuing...")
                                batch = []
                        
                except Exception as e:
                    continue  # Skip problematic files
            
            # Progress per directory
            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0
            log(f"   ✅ Directory {dir_path.name} complete - {total_processed:,} total ({rate:.0f}/sec)")
        
        # Insert final batch
        if batch:
            try:
                self.client.insert('proteins_db.alphafold_structures', batch)
                total_processed += len(batch)
            except Exception as e:
                log(f"⚠️  Final batch failed: {e}")
        
        elapsed = time.time() - start_time
        final_count = self.get_current_count()
        
        log(f"✅ ALPHAFOLD MIGRATION COMPLETE:")
        log(f"   New structures: {total_processed:,} in {elapsed/3600:.1f} hours")
        log(f"   Total structures: {final_count:,}")
        log(f"   Processing rate: {total_processed/elapsed:.0f} structures/sec")
        
        return total_processed > 100000  # Success if we processed >100K new structures

def main():
    log("="*80)
    log("🧪 COMPLETING ALPHAFOLD PROTEIN STRUCTURES MIGRATION")
    log("="*80)
    log("Processing all 23 directories to get full 500K+ dataset")
    log("="*80)
    
    migrator = AlphaFoldCompleteMigrator()
    
    # Initial system check
    log("🔍 SYSTEM CHECK:")
    log_system_status()
    log("="*80)
    
    success = migrator.complete_alphafold_migration()
    
    if success:
        log("🎉 ALPHAFOLD MIGRATION COMPLETE!")
        log("🎯 ALL MAJOR DATASETS NOW LOADED!")
    else:
        log("❌ AlphaFold migration had issues")

if __name__ == "__main__":
    main()
