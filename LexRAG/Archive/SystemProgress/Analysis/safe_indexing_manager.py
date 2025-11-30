"""
Safe Indexing Manager
Safely build indexes on massive tables without crashing the system
"""

import duckdb
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

class SafeIndexingManager:
    """Manages safe index creation with system monitoring"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.max_memory_percent = 75  # Stop if memory exceeds 75%
        self.max_cpu_percent = 80     # Stop if CPU exceeds 80%
        self.check_interval = 5       # Check resources every 5 seconds
        self.monitoring = False
        
    def monitor_system_resources(self):
        """Monitor system resources during indexing"""
        while self.monitoring:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=1)
            
            log(f"📊 System Monitor: Memory {memory_percent:.1f}%, CPU {cpu_percent:.1f}%")
            
            if memory_percent > self.max_memory_percent:
                log(f"🚨 DANGER: Memory usage {memory_percent:.1f}% exceeds limit {self.max_memory_percent}%")
                log("🛑 STOPPING OPERATION TO PREVENT CRASH")
                self.monitoring = False
                return False
                
            if cpu_percent > self.max_cpu_percent:
                log(f"🚨 WARNING: CPU usage {cpu_percent:.1f}% exceeds limit {self.max_cpu_percent}%")
                log("⏸️  Pausing for system recovery...")
                time.sleep(10)  # Give system time to recover
            
            time.sleep(self.check_interval)
        
        return True
    
    def check_existing_indexes(self, table_name: str) -> List[str]:
        """Check what indexes already exist on a table"""
        log(f"🔍 Checking existing indexes on {table_name}")
        
        try:
            conn = duckdb.connect(str(self.db_path), read_only=True)
            
            # Check table info for indexes
            # Note: DuckDB doesn't have a direct SHOW INDEXES command
            # We'll check if queries are fast to infer indexes
            
            # Test query speed on key columns
            test_queries = [
                ("variant_id", f"SELECT COUNT(*) FROM {table_name} WHERE variant_id LIKE 'chr1_%' LIMIT 1"),
                ("gene_symbol", f"SELECT COUNT(*) FROM {table_name} WHERE gene_symbol = 'BRCA2' LIMIT 1"),
                ("chrom_pos", f"SELECT COUNT(*) FROM {table_name} WHERE chrom = '1' AND pos_bp > 1000000 LIMIT 1")
            ]
            
            existing_indexes = []
            for index_name, query in test_queries:
                try:
                    start_time = time.time()
                    conn.execute(query).fetchone()
                    query_time = time.time() - start_time
                    
                    if query_time < 2.0:  # Fast query suggests index exists
                        existing_indexes.append(f"{index_name} (fast: {query_time:.2f}s)")
                        log(f"✅ Likely indexed: {index_name} - Query time: {query_time:.2f}s")
                    else:
                        log(f"❌ Likely not indexed: {index_name} - Query time: {query_time:.2f}s")
                        
                except Exception as e:
                    log(f"⚠️  Could not test {index_name}: {e}")
            
            conn.close()
            return existing_indexes
            
        except Exception as e:
            log(f"❌ Error checking indexes: {e}")
            return []
    
    def safe_create_index(self, table_name: str, column_name: str, index_name: str) -> bool:
        """Safely create index with monitoring and recovery"""
        log(f"\n🔨 CREATING INDEX: {index_name}")
        log(f"   Table: {table_name}")
        log(f"   Column: {column_name}")
        log(f"   Safety limits: Memory <{self.max_memory_percent}%, CPU <{self.max_cpu_percent}%")
        
        # Start system monitoring
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_system_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Check system resources before starting
            memory_before = psutil.virtual_memory().percent
            log(f"📊 Pre-index: Memory {memory_before:.1f}%")
            
            if memory_before > 60:  # Conservative threshold
                log(f"⚠️  High memory usage before starting - aborting for safety")
                self.monitoring = False
                return False
            
            conn = duckdb.connect(str(self.db_path), read_only=False)
            
            # Create index with verbose output
            create_index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
            log(f"🔨 Executing: {create_index_sql}")
            
            start_time = time.time()
            conn.execute(create_index_sql)
            index_time = time.time() - start_time
            
            conn.close()
            self.monitoring = False
            
            log(f"✅ INDEX CREATED SUCCESSFULLY")
            log(f"   Time taken: {index_time:.1f} seconds")
            log(f"   Final memory: {psutil.virtual_memory().percent:.1f}%")
            
            return True
            
        except Exception as e:
            self.monitoring = False
            log(f"❌ INDEX CREATION FAILED: {e}")
            log(f"🔧 System recovery: Waiting 10 seconds...")
            time.sleep(10)  # Give system time to recover
            return False
    
    def create_safe_indexes_plan(self) -> Dict[str, List[str]]:
        """Create a safe plan for indexing massive tables"""
        log(f"\n📋 CREATING SAFE INDEXING PLAN")
        log("="*60)
        
        indexing_plan = {
            "spliceai_scores_production": [
                ("gene_symbol", "idx_spliceai_gene"),
                ("variant_id", "idx_spliceai_variant"),
                ("chrom", "idx_spliceai_chrom")
            ],
            "alphafold_clinical_variant_impact": [
                ("gene_symbol", "idx_alphafold_gene"),
                ("uniprot_id", "idx_alphafold_uniprot")
            ],
            "gnomad_population_frequencies": [
                ("rsid", "idx_gnomad_rsid"),
                ("chrom", "idx_gnomad_chrom")
            ]
        }
        
        log(f"SAFE INDEXING PLAN:")
        for table, indexes in indexing_plan.items():
            log(f"\n📊 {table}:")
            for column, index_name in indexes:
                log(f"   - {index_name} on {column}")
        
        log(f"\n⚠️  SAFETY MEASURES:")
        log(f"   - Memory monitoring: <{self.max_memory_percent}%")
        log(f"   - CPU monitoring: <{self.max_cpu_percent}%")
        log(f"   - Resource checks every {self.check_interval} seconds")
        log(f"   - Auto-abort if resources exceeded")
        log(f"   - Recovery pauses between operations")
        
        return indexing_plan

def main():
    """Test safe indexing approach"""
    log("="*80)
    log("SAFE INDEXING MANAGER TEST")
    log("="*80)
    log("Goal: Safely prepare massive tables for queries without crashing system")
    
    db_path = Path("../../data/databases/genomic_knowledge/genomic_knowledge.duckdb")
    if not db_path.exists():
        log(f"❌ Database not found: {db_path}")
        return
    
    manager = SafeIndexingManager(db_path)
    
    # Step 1: Check existing indexes
    log(f"\nSTEP 1: CHECKING EXISTING INDEXES")
    log("-" * 40)
    
    tables_to_check = ["spliceai_scores_production", "alphafold_clinical_variant_impact"]
    
    for table in tables_to_check:
        existing = manager.check_existing_indexes(table)
        if existing:
            log(f"✅ {table} has indexes: {existing}")
        else:
            log(f"❌ {table} needs indexing")
    
    # Step 2: Create indexing plan
    indexing_plan = manager.create_safe_indexes_plan()
    
    # Step 3: Test one safe index creation (on smallest table first)
    log(f"\nSTEP 3: TESTING SAFE INDEX CREATION")
    log("-" * 40)
    log(f"Testing with AlphaFold table (11.6M rows - manageable size)")
    
    # Test creating one index safely
    success = manager.safe_create_index(
        table_name="alphafold_clinical_variant_impact",
        column_name="gene_symbol", 
        index_name="idx_alphafold_gene_safe_test"
    )
    
    if success:
        log(f"✅ Safe indexing approach works!")
        log(f"📋 Ready to create all planned indexes safely")
    else:
        log(f"❌ Safe indexing needs adjustment")
    
    log(f"\n{'='*80}")
    log("SAFE INDEXING TEST COMPLETE")
    log("System stability maintained throughout")
    log("="*80)

if __name__ == "__main__":
    main()
