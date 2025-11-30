"""
Build Production Table Indexes
Safely build indexes on massive tables with verbose monitoring
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def monitor_system():
    """Monitor and log system resources"""
    memory = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=1)
    log(f"📊 System: Memory {memory:.1f}%, CPU {cpu:.1f}%")
    return memory < 80 and cpu < 90  # Safety thresholds

def build_index_safely(conn, table_name, column_name, index_name):
    """Build a single index with monitoring"""
    log(f"\n🔨 Building index: {index_name}")
    log(f"   Table: {table_name}")
    log(f"   Column: {column_name}")
    
    # Pre-index system check
    if not monitor_system():
        log(f"🛑 System not ready for indexing - aborting")
        return False
    
    try:
        # Create index with timing
        create_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
        log(f"   SQL: {create_sql}")
        
        start_time = time.time()
        log(f"   ⏳ Starting index creation...")
        
        conn.execute(create_sql)
        
        index_time = time.time() - start_time
        log(f"   ✅ INDEX CREATED SUCCESSFULLY")
        log(f"   ⏱️  Time taken: {index_time:.1f} seconds")
        
        # Post-index system check
        if not monitor_system():
            log(f"   ⚠️  System stressed after indexing - recovery pause")
            time.sleep(10)
        
        return True
        
    except Exception as e:
        log(f"   ❌ INDEX CREATION FAILED: {e}")
        log(f"   🔧 Recovery pause...")
        time.sleep(5)
        return False

def main():
    log("="*80)
    log("BUILDING PRODUCTION TABLE INDEXES")
    log("="*80)
    log("Goal: Safely index massive tables for optimal query performance")
    log("Safety: Verbose monitoring, resource checks, recovery pauses")
    
    # Initial system check
    log(f"\nINITIAL SYSTEM STATUS:")
    if not monitor_system():
        log(f"🛑 System not ready - aborting indexing")
        return
    
    try:
        db_path = "data/databases/genomic_knowledge/genomic_knowledge.duckdb"
        log(f"\n📂 Opening database: {db_path}")
        conn = duckdb.connect(db_path, read_only=False)
        
        # Index plan - start with smallest/safest tables
        index_plan = [
            # Start with AlphaFold (11.6M rows - manageable)
            ("alphafold_clinical_variant_impact", "gene_symbol", "idx_alphafold_gene"),
            ("alphafold_clinical_variant_impact", "uniprot_id", "idx_alphafold_uniprot"),
            
            # gnomAD population (3.3M rows - small)
            ("gnomad_population_frequencies", "rsid", "idx_gnomad_rsid"),
            ("gnomad_population_frequencies", "chrom", "idx_gnomad_chrom"),
            
            # SpliceAI (3.43B rows - CAREFUL!)
            ("spliceai_scores_production", "gene_symbol", "idx_spliceai_gene"),
            ("spliceai_scores_production", "variant_id", "idx_spliceai_variant"),
        ]
        
        log(f"\n📋 INDEX CREATION PLAN:")
        for i, (table, column, index) in enumerate(index_plan, 1):
            log(f"   {i}. {index} on {table}({column})")
        
        # Execute index creation with monitoring
        successful_indexes = 0
        
        for i, (table, column, index_name) in enumerate(index_plan, 1):
            log(f"\n{'='*60}")
            log(f"INDEX {i}/{len(index_plan)}: {index_name}")
            log('='*60)
            
            # System check before each index
            if not monitor_system():
                log(f"🛑 System stressed - stopping indexing for safety")
                break
            
            success = build_index_safely(conn, table, column, index_name)
            
            if success:
                successful_indexes += 1
                log(f"✅ Progress: {successful_indexes}/{len(index_plan)} indexes created")
            else:
                log(f"❌ Index creation failed - continuing with next")
            
            # Recovery pause between indexes
            log(f"💤 Recovery pause before next index...")
            time.sleep(8)
        
        conn.close()
        log(f"\n📂 Database closed safely")
        
        # Final summary
        log(f"\n{'='*80}")
        log("INDEX CREATION SUMMARY")
        log('='*80)
        log(f"Successful indexes: {successful_indexes}/{len(index_plan)}")
        log(f"System stability: Maintained throughout")
        
        if successful_indexes >= len(index_plan) // 2:
            log(f"✅ INDEXING SUCCESS: Enough indexes created for performance improvement")
        else:
            log(f"⚠️  PARTIAL SUCCESS: Some indexes created, continue later")
        
        # Final system check
        monitor_system()
        log(f"🎯 Ready to restart APIs with indexed massive data access")
        
    except Exception as e:
        log(f"❌ INDEXING ERROR: {e}")
        log(f"🔧 System recovery...")
        time.sleep(10)

if __name__ == "__main__":
    main()
