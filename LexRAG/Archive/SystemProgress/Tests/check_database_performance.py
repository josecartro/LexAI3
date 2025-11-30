import duckdb
import time

print("DATABASE PERFORMANCE ANALYSIS")
print("="*40)

print("Database types in use:")
print("  DuckDB: Main data storage (genomic_knowledge.duckdb)")
print("  Neo4j: Graph relationships")
print("  Qdrant: Vector search")

print("\nTesting DuckDB performance:")

try:
    conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
    
    # Test 1: Simple indexed query
    start = time.time()
    result = conn.execute("SELECT COUNT(*) FROM variants_clinical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
    time1 = time.time() - start
    print(f"  Simple lookup: {result:,} rows in {time1:.3f}s")
    
    # Test 2: Optimized table query
    start = time.time()
    result2 = conn.execute("SELECT COUNT(*) FROM spliceai_practical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
    time2 = time.time() - start
    print(f"  SpliceAI optimized: {result2:,} rows in {time2:.3f}s")
    
    # Test 3: Join query (more complex)
    start = time.time()
    result3 = conn.execute("""
        SELECT COUNT(*) 
        FROM variants_clinical vc
        JOIN spliceai_practical sp ON vc.gene_symbol = sp.gene_symbol
        WHERE vc.gene_symbol = 'BRCA2'
    """).fetchone()[0]
    time3 = time.time() - start
    print(f"  Join query: {result3:,} rows in {time3:.3f}s")
    
    conn.close()
    
    print(f"\nPERFORMANCE ASSESSMENT:")
    if time1 < 0.1 and time2 < 0.1:
        print("  ✅ DuckDB performance is good (<0.1s)")
    elif time1 < 0.5 and time2 < 0.5:
        print("  ⚠️  DuckDB performance is acceptable (<0.5s)")
    else:
        print(f"  ❌ DuckDB performance is slow (>{time1:.3f}s, {time2:.3f}s)")
        print("     Possible issues: No indexes, table too large, disk I/O")
    
except Exception as e:
    print(f"  ERROR: {e}")

print(f"\nRECOMMENDATION:")
print("For sub-1s performance, we need:")
print("  - Proper indexes on all lookup columns") 
print("  - Smaller, focused tables")
print("  - Simple queries without complex JOINs")
print("  - Consider faster database for hot data")
