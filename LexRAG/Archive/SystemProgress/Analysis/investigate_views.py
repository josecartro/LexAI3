"""
Investigate VIEW Structure
Find underlying base tables that need indexing
"""

import duckdb
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def investigate_views():
    """Investigate which tables are views and what base tables they use"""
    log("="*80)
    log("INVESTIGATING VIEW STRUCTURE")
    log("="*80)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Get all tables and their types
        log("📊 CHECKING ALL TABLE TYPES:")
        tables_info = conn.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'main'
            ORDER BY table_type, table_name
        """).fetchall()
        
        base_tables = []
        views = []
        
        for table_name, table_type in tables_info:
            if table_type == 'BASE TABLE':
                base_tables.append(table_name)
            elif table_type == 'VIEW':
                views.append(table_name)
        
        log(f"   Base tables: {len(base_tables)}")
        log(f"   Views: {len(views)}")
        
        # Focus on problematic tables
        problem_tables = ['alphafold_clinical_variant_impact', 'spliceai_scores_production']
        
        log(f"\n🔍 INVESTIGATING PROBLEM TABLES:")
        for table in problem_tables:
            table_type = None
            for name, ttype in tables_info:
                if name == table:
                    table_type = ttype
                    break
            
            log(f"\n📋 {table}:")
            log(f"   Type: {table_type}")
            
            if table_type == 'VIEW':
                log(f"   ❌ PROBLEM: This is a VIEW, not a base table")
                
                # Try to get view definition
                try:
                    view_def = conn.execute(f"SELECT sql FROM sqlite_master WHERE name = '{table}' AND type = 'view'").fetchone()
                    if view_def:
                        sql_def = view_def[0]
                        log(f"   📝 View definition: {sql_def[:200]}...")
                        
                        # Look for underlying table names in the SQL
                        if 'FROM ' in sql_def.upper():
                            from_part = sql_def.upper().split('FROM ')[1].split(' ')[0]
                            log(f"   🎯 Underlying table: {from_part}")
                    else:
                        log(f"   ❌ Cannot get view definition")
                        
                except Exception as e:
                    log(f"   ❌ Error getting view definition: {e}")
                    
            elif table_type == 'BASE TABLE':
                log(f"   ✅ This is a BASE TABLE - can be indexed")
                
                # Check if it already has indexes
                try:
                    # Test query speed to infer indexing
                    start_time = time.time()
                    conn.execute(f"SELECT COUNT(*) FROM {table} WHERE gene_symbol = 'BRCA2'").fetchone()
                    query_time = time.time() - start_time
                    
                    if query_time < 1.0:
                        log(f"   ✅ Fast gene lookup ({query_time:.3f}s) - likely indexed")
                    else:
                        log(f"   ⚠️  Slow gene lookup ({query_time:.3f}s) - needs indexing")
                        
                except Exception as e:
                    log(f"   ❌ Cannot test query speed: {e}")
        
        # List base tables that might need indexing
        log(f"\n📋 BASE TABLES THAT COULD BE INDEXED:")
        large_base_tables = []
        
        for table in base_tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                if count > 1000000:  # Tables with >1M rows
                    large_base_tables.append((table, count))
            except:
                pass
        
        # Sort by size
        large_base_tables.sort(key=lambda x: x[1], reverse=True)
        
        for table, count in large_base_tables[:10]:  # Top 10 largest
            log(f"   {table}: {count:,} rows")
        
        conn.close()
        
    except Exception as e:
        log(f"❌ Investigation error: {e}")

def check_memory_settings():
    """Check optimal memory settings for indexing"""
    log(f"\n💾 MEMORY OPTIMIZATION ANALYSIS:")
    
    # System memory info
    import psutil
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    available_memory_gb = psutil.virtual_memory().available / (1024**3)
    
    log(f"   System total memory: {total_memory_gb:.1f} GB")
    log(f"   Available memory: {available_memory_gb:.1f} GB")
    log(f"   Windows overhead: ~{total_memory_gb - available_memory_gb:.1f} GB")
    
    # Recommend DuckDB memory settings
    safe_memory_gb = min(available_memory_gb * 0.7, 16)  # Use 70% of available, max 16GB
    
    log(f"\n💡 RECOMMENDED DUCKDB SETTINGS:")
    log(f"   SET memory_limit='{safe_memory_gb:.0f}GB'")
    log(f"   SET threads=1  -- Single thread for large operations")
    log(f"   SET preserve_insertion_order=false  -- Save memory")

def main():
    log("="*80)
    log("VIEW AND INDEXING INVESTIGATION")
    log("="*80)
    log("Goal: Find underlying tables and optimal indexing strategy")
    
    investigate_views()
    check_memory_settings()
    
    log(f"\n{'='*80}")
    log("INVESTIGATION COMPLETE")
    log("Found underlying table structure and memory optimization strategy")
    log("="*80)

if __name__ == "__main__":
    main()
