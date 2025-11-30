"""
SpliceAI Index Creation Strategies
Try multiple approaches to index the 3.43B row SpliceAI table
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def monitor_resources():
    """Monitor system resources"""
    memory = psutil.virtual_memory().percent
    available_gb = psutil.virtual_memory().available / (1024**3)
    log(f"📊 Memory: {memory:.1f}%, Available: {available_gb:.1f}GB")
    return memory < 85

def strategy_1_maximum_memory():
    """Strategy 1: Use maximum available memory"""
    log("\n🚀 STRATEGY 1: MAXIMUM MEMORY ALLOCATION")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Use maximum safe memory
        available_gb = psutil.virtual_memory().available / (1024**3)
        max_memory = min(available_gb * 0.9, 20)  # Use 90% of available, max 20GB
        
        log(f"🔧 Setting maximum memory: {max_memory:.0f}GB")
        conn.execute(f"SET memory_limit='{max_memory:.0f}GB'")
        conn.execute("SET threads=1")
        conn.execute("SET preserve_insertion_order=false")
        
        # Try creating SpliceAI gene_symbol index with max memory
        log(f"🔨 Attempting SpliceAI gene_symbol index with {max_memory:.0f}GB...")
        
        start_time = time.time()
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spliceai_gene_max_mem ON spliceai_scores_production(gene_symbol)")
        index_time = time.time() - start_time
        
        conn.close()
        
        log(f"✅ SUCCESS: SpliceAI gene index created in {index_time:.1f}s")
        return True
        
    except Exception as e:
        log(f"❌ Strategy 1 failed: {e}")
        if "memory" in str(e).lower():
            log(f"💡 Memory still insufficient even with {max_memory:.0f}GB")
        return False

def strategy_2_external_sorting():
    """Strategy 2: Use external sorting for large index"""
    log("\n💾 STRATEGY 2: EXTERNAL SORTING")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Enable external sorting (spill to disk)
        log(f"🔧 Enabling external sorting (disk spill)...")
        conn.execute("SET memory_limit='8GB'")  # Lower memory forces external sort
        conn.execute("SET threads=1")
        conn.execute("SET preserve_insertion_order=false")
        conn.execute("SET temp_directory='temp_indexing'")  # Specify temp directory
        
        log(f"🔨 Creating SpliceAI index with external sorting...")
        
        start_time = time.time()
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spliceai_gene_external ON spliceai_scores_production(gene_symbol)")
        index_time = time.time() - start_time
        
        conn.close()
        
        log(f"✅ SUCCESS: SpliceAI gene index created with external sort in {index_time:.1f}s")
        return True
        
    except Exception as e:
        log(f"❌ Strategy 2 failed: {e}")
        return False

def strategy_3_alternative_column():
    """Strategy 3: Try indexing different column that might be smaller"""
    log("\n🎯 STRATEGY 3: ALTERNATIVE COLUMN INDEX")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Check column characteristics
        log(f"🔍 Analyzing SpliceAI columns for indexing...")
        
        # Check distinct values in different columns
        columns_to_check = ['chrom', 'variant_type', 'gene_symbol']
        
        for column in columns_to_check:
            try:
                distinct_count = conn.execute(f"SELECT COUNT(DISTINCT {column}) FROM spliceai_scores_production").fetchone()[0]
                log(f"   {column}: {distinct_count:,} distinct values")
                
                # Lower cardinality = better for indexing
                if distinct_count < 50000:  # Good for indexing
                    log(f"   ✅ {column} good for indexing (low cardinality)")
                    
                    # Try creating index on this column
                    index_name = f"idx_spliceai_{column}"
                    log(f"   🔨 Creating index: {index_name}")
                    
                    start_time = time.time()
                    conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON spliceai_scores_production({column})")
                    index_time = time.time() - start_time
                    
                    log(f"   ✅ SUCCESS: {column} index created in {index_time:.1f}s")
                    
                else:
                    log(f"   ⚠️  {column} high cardinality - might be difficult")
                    
            except Exception as e:
                log(f"   ❌ {column} analysis failed: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        log(f"❌ Strategy 3 failed: {e}")
        return False

def strategy_4_test_existing_performance():
    """Strategy 4: Test if we actually need indexes - maybe it's already fast enough"""
    log("\n🧪 STRATEGY 4: TEST EXISTING PERFORMANCE")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Test various query patterns to see what's already fast
        test_queries = [
            ("Gene lookup", "SELECT COUNT(*) FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2'"),
            ("Chromosome lookup", "SELECT COUNT(*) FROM spliceai_scores_production WHERE chrom = '17'"),
            ("High score lookup", "SELECT * FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2' AND (ABS(acceptor_gain_score) > 0.5 OR ABS(donor_gain_score) > 0.5) LIMIT 10")
        ]
        
        log(f"🧪 Testing query performance without additional indexes:")
        
        for query_name, query_sql in test_queries:
            try:
                start_time = time.time()
                result = conn.execute(query_sql).fetchall()
                query_time = time.time() - start_time
                
                result_count = len(result) if isinstance(result, list) else result[0][0] if result else 0
                
                log(f"   {query_name}: {result_count:,} results in {query_time:.3f}s")
                
                if query_time < 5.0:
                    log(f"   ✅ Already fast enough - no index needed")
                else:
                    log(f"   ⚠️  Could benefit from indexing")
                    
            except Exception as e:
                log(f"   ❌ {query_name} failed: {e}")
        
        conn.close()
        
        log(f"\n💡 CONCLUSION: Check if existing performance is acceptable")
        return True
        
    except Exception as e:
        log(f"❌ Strategy 4 failed: {e}")
        return False

def main():
    log("="*80)
    log("SPLICEAI INDEX CREATION STRATEGIES")
    log("="*80)
    log("Goal: Try multiple approaches to index 3.43B row SpliceAI table")
    
    # Initial system check
    if not monitor_resources():
        log("🛑 System not ready")
        return
    
    strategies = [
        ("Maximum Memory", strategy_1_maximum_memory),
        ("External Sorting", strategy_2_external_sorting), 
        ("Alternative Columns", strategy_3_alternative_column),
        ("Test Existing Performance", strategy_4_test_existing_performance)
    ]
    
    successful_strategies = 0
    
    for strategy_name, strategy_func in strategies:
        log(f"\n{'='*60}")
        log(f"TRYING: {strategy_name}")
        log('='*60)
        
        if not monitor_resources():
            log(f"🛑 System stressed - stopping strategies")
            break
        
        try:
            success = strategy_func()
            if success:
                successful_strategies += 1
                log(f"✅ {strategy_name}: SUCCESS")
            else:
                log(f"❌ {strategy_name}: FAILED")
                
        except Exception as e:
            log(f"❌ {strategy_name}: ERROR - {e}")
        
        # Recovery pause between strategies
        log(f"💤 Recovery pause between strategies...")
        time.sleep(10)
    
    log(f"\n{'='*80}")
    log("SPLICEAI INDEXING STRATEGIES COMPLETE")
    log('='*80)
    log(f"Successful strategies: {successful_strategies}/{len(strategies)}")
    
    if successful_strategies > 0:
        log(f"✅ At least one approach worked for SpliceAI access")
    else:
        log(f"❌ All strategies failed - may need different approach")
    
    # Final system check
    monitor_resources()

if __name__ == "__main__":
    main()

