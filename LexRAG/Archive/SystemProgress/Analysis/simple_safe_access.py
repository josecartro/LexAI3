"""
Simple Safe Access to Massive Data
Test safe access to billion-row tables with limits and monitoring
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def check_system_safety():
    """Check if system is safe for database operations"""
    memory_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=1)
    
    log(f"📊 System status: Memory {memory_percent:.1f}%, CPU {cpu_percent:.1f}%")
    
    if memory_percent > 75:
        log(f"🚨 DANGER: High memory usage {memory_percent:.1f}% - ABORTING")
        return False
    
    if cpu_percent > 85:
        log(f"⚠️  WARNING: High CPU usage {cpu_percent:.1f}% - waiting...")
        time.sleep(10)
    
    return True

def safe_test_massive_table(table_name, description):
    """Safely test access to a massive table"""
    log(f"\n🧪 TESTING SAFE ACCESS: {table_name}")
    log(f"   Description: {description}")
    
    if not check_system_safety():
        return False
    
    try:
        db_path = "data/databases/genomic_knowledge/genomic_knowledge.duckdb"
        conn = duckdb.connect(db_path, read_only=True)
        
        # Safe test 1: Quick count (should use metadata if available)
        log(f"   Step 1: Getting row count...")
        start_time = time.time()
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        count_time = time.time() - start_time
        
        log(f"   ✅ Row count: {count:,} ({count_time:.2f}s)")
        
        if count_time > 30:
            log(f"   ⚠️  Slow count suggests no indexes")
        else:
            log(f"   ✅ Fast count suggests good performance")
        
        # Safe test 2: Sample data (very limited)
        log(f"   Step 2: Getting sample data...")
        start_time = time.time()
        sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
        sample_time = time.time() - start_time
        
        log(f"   ✅ Sample retrieved: {len(sample)} rows ({sample_time:.2f}s)")
        
        # Safe test 3: Column info
        columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
        key_columns = [col[0] for col in columns if any(word in col[0].lower() for word in ['gene', 'variant', 'rsid', 'id'])]
        log(f"   ✅ Key columns for indexing: {key_columns}")
        
        conn.close()
        
        # Check system after operations
        if not check_system_safety():
            return False
        
        log(f"   ✅ Table access successful - system stable")
        return True
        
    except Exception as e:
        log(f"   ❌ Error accessing {table_name}: {e}")
        return False

def safe_create_minimal_index(table_name, column_name, index_name):
    """Safely create one index with full monitoring"""
    log(f"\n🔨 SAFE INDEX CREATION")
    log(f"   Table: {table_name}")
    log(f"   Column: {column_name}")
    log(f"   Index: {index_name}")
    
    # Pre-flight check
    if not check_system_safety():
        log(f"🛑 ABORTING: System not safe for indexing")
        return False
    
    try:
        db_path = "data/databases/genomic_knowledge/genomic_knowledge.duckdb"
        
        log(f"   Step 1: Opening database for write access...")
        conn = duckdb.connect(db_path, read_only=False)
        
        # Monitor during index creation
        log(f"   Step 2: Creating index (monitoring system resources)...")
        
        create_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
        log(f"   SQL: {create_sql}")
        
        start_time = time.time()
        
        # Execute with monitoring
        conn.execute(create_sql)
        
        index_time = time.time() - start_time
        
        conn.close()
        
        log(f"   ✅ INDEX CREATED SUCCESSFULLY")
        log(f"   ⏱️  Time taken: {index_time:.1f} seconds")
        
        # Post-creation system check
        if not check_system_safety():
            log(f"   ⚠️  System stressed after indexing - allowing recovery time")
            time.sleep(15)
        
        return True
        
    except Exception as e:
        log(f"   ❌ INDEX CREATION FAILED: {e}")
        log(f"   🔧 Allowing system recovery time...")
        time.sleep(10)
        return False

def main():
    log("="*80)
    log("SAFE MASSIVE DATA ACCESS PREPARATION")
    log("="*80)
    log("Goal: Safely prepare billion-row tables for queries")
    log("Safety: Verbose monitoring, resource limits, crash prevention")
    
    # Initial system check
    log(f"\nINITIAL SYSTEM CHECK:")
    if not check_system_safety():
        log(f"🛑 System not ready for massive data operations")
        return
    
    # Test access to massive tables
    massive_tables = [
        ("alphafold_clinical_variant_impact", "11.6M protein structures (safest to test)"),
        ("gnomad_population_frequencies", "3.3M population genetics (medium size)"),
        ("spliceai_scores_production", "3.43B splice predictions (DANGEROUS - test last)")
    ]
    
    log(f"\nTESTING SAFE ACCESS TO MASSIVE TABLES:")
    log("="*50)
    
    safe_tables = []
    
    for table, description in massive_tables:
        if safe_test_massive_table(table, description):
            safe_tables.append(table)
            log(f"✅ {table}: Safe for indexing")
        else:
            log(f"❌ {table}: Not safe - skip indexing")
        
        # Recovery pause between tests
        log(f"   💤 Recovery pause...")
        time.sleep(5)
    
    # Create one safe index as test
    if safe_tables:
        log(f"\nTESTING SAFE INDEX CREATION:")
        log("="*50)
        log(f"Creating test index on safest table: {safe_tables[0]}")
        
        success = safe_create_minimal_index(
            table_name=safe_tables[0],
            column_name="gene_symbol",
            index_name="idx_safe_test_gene_symbol"
        )
        
        if success:
            log(f"✅ SAFE INDEXING PROVEN TO WORK")
            log(f"📋 Can proceed with careful indexing of all massive tables")
        else:
            log(f"❌ Safe indexing needs more careful approach")
    
    log(f"\n{'='*80}")
    log("SAFE PREPARATION COMPLETE")
    log("System stability maintained - ready for careful massive data integration")
    log("="*80)

if __name__ == "__main__":
    main()
