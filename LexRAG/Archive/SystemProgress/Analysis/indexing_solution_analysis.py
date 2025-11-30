"""
Indexing Solution Analysis
Analyze why indexes failed and create solutions for massive data access
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def analyze_indexing_failures():
    """Analyze why indexes failed and find solutions"""
    log("="*80)
    log("ANALYZING INDEXING FAILURES")
    log("="*80)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Check DuckDB settings that might help
        log("📊 CHECKING DUCKDB CONFIGURATION:")
        
        # Check memory limit
        memory_limit = conn.execute("SELECT current_setting('memory_limit')").fetchone()[0]
        log(f"   Current memory limit: {memory_limit}")
        
        # Check thread count
        threads = conn.execute("SELECT current_setting('threads')").fetchone()[0]
        log(f"   Current threads: {threads}")
        
        # Check if we can increase memory limit
        log(f"\n🔧 ATTEMPTING MEMORY OPTIMIZATION:")
        try:
            # Increase memory limit for indexing
            conn.execute("SET memory_limit='8GB'")
            new_limit = conn.execute("SELECT current_setting('memory_limit')").fetchone()[0]
            log(f"   ✅ Memory limit increased to: {new_limit}")
        except Exception as e:
            log(f"   ❌ Cannot increase memory limit: {e}")
        
        # Reduce threads to save memory
        try:
            conn.execute("SET threads=2")
            new_threads = conn.execute("SELECT current_setting('threads')").fetchone()[0]
            log(f"   ✅ Threads reduced to: {new_threads}")
        except Exception as e:
            log(f"   ❌ Cannot reduce threads: {e}")
        
        # Test why AlphaFold index failed
        log(f"\n🔍 ANALYZING ALPHAFOLD TABLE TYPE:")
        try:
            table_info = conn.execute("SELECT table_type FROM information_schema.tables WHERE table_name = 'alphafold_clinical_variant_impact'").fetchone()
            if table_info:
                table_type = table_info[0]
                log(f"   AlphaFold table type: {table_type}")
                
                if table_type != 'BASE TABLE':
                    log(f"   ❌ ISSUE: Table is {table_type}, not BASE TABLE")
                    log(f"   💡 SOLUTION: May need to recreate as base table")
                else:
                    log(f"   ✅ Table type is correct for indexing")
            else:
                log(f"   ❌ Cannot determine table type")
                
        except Exception as e:
            log(f"   ❌ Error checking table type: {e}")
        
        # Test batch indexing approach for SpliceAI
        log(f"\n🧪 TESTING BATCH INDEXING APPROACH:")
        try:
            # Check if we can create index with specific memory settings
            log(f"   Attempting SpliceAI index with optimized settings...")
            
            # Disable insertion order preservation (saves memory)
            conn.execute("SET preserve_insertion_order=false")
            log(f"   ✅ Disabled insertion order preservation")
            
            # Try creating the index again with optimizations
            start_time = time.time()
            
            create_sql = "CREATE INDEX IF NOT EXISTS idx_spliceai_variant_optimized ON spliceai_scores_production(variant_id)"
            log(f"   SQL: {create_sql}")
            log(f"   ⏳ Creating optimized SpliceAI index...")
            
            conn.execute(create_sql)
            
            index_time = time.time() - start_time
            log(f"   ✅ OPTIMIZED INDEX CREATED: {index_time:.1f} seconds")
            
        except Exception as e:
            log(f"   ❌ Optimized indexing failed: {e}")
            
            # Check if it's a memory issue
            if "out of memory" in str(e).lower():
                log(f"   💡 SOLUTION: Need batch indexing or external sorting")
                log(f"   🔧 Alternative: Create partial indexes on subsets")
            elif "base table" in str(e).lower():
                log(f"   💡 SOLUTION: Need to convert to base table first")
            else:
                log(f"   💡 SOLUTION: Unknown issue - may need different approach")
        
        conn.close()
        
    except Exception as e:
        log(f"❌ Database access error: {e}")

def propose_indexing_solutions():
    """Propose solutions for successful indexing"""
    log(f"\n{'='*80}")
    log("INDEXING SOLUTION PROPOSALS")
    log('='*80)
    
    solutions = [
        {
            'solution': 'Memory Optimization',
            'approach': 'Increase DuckDB memory limit, reduce threads, disable features',
            'commands': [
                "SET memory_limit='16GB'",
                "SET threads=1", 
                "SET preserve_insertion_order=false"
            ],
            'risk': 'LOW',
            'effectiveness': 'MEDIUM'
        },
        {
            'solution': 'Partial Indexing',
            'approach': 'Create indexes on subsets of data (by chromosome, gene)',
            'commands': [
                "CREATE INDEX idx_splice_chr1 ON spliceai_scores_production(variant_id) WHERE chrom='1'",
                "CREATE INDEX idx_splice_chr2 ON spliceai_scores_production(variant_id) WHERE chrom='2'"
            ],
            'risk': 'LOW',
            'effectiveness': 'HIGH'
        },
        {
            'solution': 'Smart Query Design',
            'approach': 'Use existing fast columns, avoid full table scans',
            'commands': [
                "SELECT * FROM spliceai_scores_production WHERE gene_symbol='BRCA2' LIMIT 100",
                "Use WHERE clauses that leverage existing structure"
            ],
            'risk': 'VERY LOW',
            'effectiveness': 'HIGH'
        },
        {
            'solution': 'External Index Creation',
            'approach': 'Create indexes offline with dedicated tools',
            'commands': [
                "Use DuckDB CLI with more memory",
                "Create indexes during maintenance windows"
            ],
            'risk': 'LOW',
            'effectiveness': 'HIGH'
        }
    ]
    
    log(f"RECOMMENDED SOLUTIONS:")
    for i, solution in enumerate(solutions, 1):
        log(f"\n{i}. {solution['solution']} (Risk: {solution['risk']}, Effect: {solution['effectiveness']})")
        log(f"   Approach: {solution['approach']}")
        log(f"   Implementation:")
        for cmd in solution['commands']:
            log(f"     - {cmd}")

def main():
    log("="*80)
    log("INDEXING SOLUTION ANALYSIS")
    log("="*80)
    log("Goal: Find solutions for successful massive data indexing")
    
    # Analyze why indexing failed
    analyze_indexing_failures()
    
    # Propose solutions
    propose_indexing_solutions()
    
    log(f"\n{'='*80}")
    log("ANALYSIS COMPLETE")
    log("Multiple solutions available for massive data access")
    log("="*80)

if __name__ == "__main__":
    main()
