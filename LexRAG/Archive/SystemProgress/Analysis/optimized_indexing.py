"""
Optimized Indexing with Proper Memory Management
Create indexes on base tables with optimal DuckDB settings
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def monitor_system():
    """Monitor system resources during indexing"""
    memory = psutil.virtual_memory().percent
    available_gb = psutil.virtual_memory().available / (1024**3)
    log(f"📊 System: Memory {memory:.1f}%, Available {available_gb:.1f}GB")
    return memory < 80

def optimize_duckdb_for_indexing(conn):
    """Apply optimal DuckDB settings for large table indexing"""
    log("🔧 OPTIMIZING DUCKDB FOR INDEXING:")
    
    try:
        # Set memory limit to safe amount (12GB of 17GB available)
        conn.execute("SET memory_limit='12GB'")
        log("   ✅ Memory limit: 12GB")
        
        # Single thread for stability
        conn.execute("SET threads=1")
        log("   ✅ Threads: 1 (stability)")
        
        # Disable insertion order to save memory
        conn.execute("SET preserve_insertion_order=false")
        log("   ✅ Insertion order: disabled (memory saving)")
        
        # Enable aggressive memory management
        conn.execute("SET max_memory='12GB'")
        log("   ✅ Max memory: 12GB")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Optimization failed: {e}")
        return False

def create_base_table_indexes():
    """Create indexes on base tables with optimized settings"""
    log("\n🔨 CREATING INDEXES ON BASE TABLES")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Apply optimizations
        if not optimize_duckdb_for_indexing(conn):
            log("❌ Cannot optimize DuckDB - aborting")
            return False
        
        # Index plan for base tables only
        index_plan = [
            # Start with smaller base tables
            {
                'table': 'clinvar_full_production',
                'column': 'gene_symbol', 
                'index': 'idx_clinvar_gene',
                'description': '3.7M variants (base table behind AlphaFold VIEW)'
            },
            {
                'table': 'clinvar_full_production',
                'column': 'rsid',
                'index': 'idx_clinvar_rsid', 
                'description': '3.7M variants - rsid lookup'
            },
            {
                'table': 'dbsnp_parquet_production',
                'column': 'rsid',
                'index': 'idx_dbsnp_rsid',
                'description': '37M variants - population data'
            },
            # SpliceAI last (biggest risk)
            {
                'table': 'spliceai_scores_production',
                'column': 'gene_symbol',
                'index': 'idx_spliceai_gene_optimized',
                'description': '3.43B splice predictions - gene lookup'
            }
        ]
        
        successful_indexes = 0
        
        for i, index_info in enumerate(index_plan, 1):
            log(f"\n{'='*50}")
            log(f"INDEX {i}/{len(index_plan)}: {index_info['index']}")
            log(f"Description: {index_info['description']}")
            log('='*50)
            
            # System check before each index
            if not monitor_system():
                log(f"🛑 System not ready - stopping for safety")
                break
            
            try:
                # Check table size
                count = conn.execute(f"SELECT COUNT(*) FROM {index_info['table']}").fetchone()[0]
                log(f"📊 Table size: {count:,} rows")
                
                # Create index with monitoring
                create_sql = f"CREATE INDEX IF NOT EXISTS {index_info['index']} ON {index_info['table']}({index_info['column']})"
                log(f"🔨 SQL: {create_sql}")
                
                start_time = time.time()
                log(f"⏳ Creating index...")
                
                conn.execute(create_sql)
                
                index_time = time.time() - start_time
                log(f"✅ INDEX CREATED SUCCESSFULLY")
                log(f"⏱️  Time: {index_time:.1f} seconds")
                
                successful_indexes += 1
                
                # Test index performance
                test_start = time.time()
                if index_info['column'] == 'gene_symbol':
                    conn.execute(f"SELECT COUNT(*) FROM {index_info['table']} WHERE gene_symbol = 'BRCA2'").fetchone()
                elif index_info['column'] == 'rsid':
                    conn.execute(f"SELECT COUNT(*) FROM {index_info['table']} WHERE rsid = 'rs7412'").fetchone()
                test_time = time.time() - test_start
                
                log(f"🧪 Index test: {test_time:.3f} seconds")
                
                # Recovery pause
                log(f"💤 Recovery pause...")
                time.sleep(5)
                
            except Exception as e:
                log(f"❌ Index creation failed: {e}")
                
                if "memory" in str(e).lower():
                    log(f"🛑 Memory issue - stopping indexing for safety")
                    break
                else:
                    log(f"⚠️  Continuing with next index...")
        
        conn.close()
        
        log(f"\n{'='*60}")
        log("OPTIMIZED INDEXING SUMMARY")
        log('='*60)
        log(f"Successful indexes: {successful_indexes}/{len(index_plan)}")
        
        if successful_indexes >= 2:
            log(f"✅ INDEXING SUCCESS: Core indexes created")
            log(f"🎯 Massive data now accessible with optimized queries")
        else:
            log(f"⚠️  PARTIAL SUCCESS: Some indexes created")
        
        return successful_indexes > 0
        
    except Exception as e:
        log(f"❌ Indexing error: {e}")
        return False

if __name__ == "__main__":
    success = create_base_table_indexes()
    if success:
        print("\n🎉 OPTIMIZED INDEXING COMPLETE!")
    else:
        print("\n❌ Indexing needs alternative approach")
