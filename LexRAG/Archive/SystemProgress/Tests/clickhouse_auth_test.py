import time
import requests
from requests.auth import HTTPBasicAuth

print("CLICKHOUSE AUTHENTICATED PERFORMANCE TEST")
print("="*50)

auth = HTTPBasicAuth('genomics', 'genomics123')

# Test 1: Create database
print("1. Creating test database...")
try:
    r = requests.post("http://localhost:8123/", data="CREATE DATABASE IF NOT EXISTS genomics_test", auth=auth)
    if r.status_code == 200:
        print("   SUCCESS: Database created")
    else:
        print(f"   FAILED: {r.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Create table
print("\n2. Creating variants table...")
create_table = """
CREATE TABLE IF NOT EXISTS genomics_test.variants (
    rsid String,
    gene_symbol String,
    clinical_significance String,
    pathogenicity_score Float32
) ENGINE = MergeTree()
ORDER BY (gene_symbol, rsid)
"""

try:
    r = requests.post("http://localhost:8123/", data=create_table, auth=auth)
    if r.status_code == 200:
        print("   SUCCESS: Table created")
    else:
        print(f"   FAILED: {r.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Insert data
print("\n3. Inserting test data...")
insert_data = """
INSERT INTO genomics_test.variants VALUES 
('rs7412', 'APOE', 'Pathogenic', 0.95),
('rs429358', 'APOE', 'Risk_factor', 0.85),
('rs80357713', 'BRCA1', 'Pathogenic', 0.99),
('rs80357906', 'BRCA2', 'Pathogenic', 0.98),
('rs11540654', 'TP53', 'Pathogenic', 0.97)
"""

try:
    r = requests.post("http://localhost:8123/", data=insert_data, auth=auth)
    if r.status_code == 200:
        print("   SUCCESS: Test data inserted")
    else:
        print(f"   FAILED: {r.status_code}")
        print(f"   Response: {r.text}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Performance queries
print("\n4. Testing query performance...")

queries = [
    ("Count variants", "SELECT COUNT(*) FROM genomics_test.variants"),
    ("Gene lookup", "SELECT * FROM genomics_test.variants WHERE gene_symbol = 'BRCA2'"),
    ("Group by gene", "SELECT gene_symbol, COUNT(*) FROM genomics_test.variants GROUP BY gene_symbol"),
    ("Filter pathogenic", "SELECT * FROM genomics_test.variants WHERE clinical_significance = 'Pathogenic'")
]

clickhouse_times = []

for query_name, query_sql in queries:
    try:
        start_time = time.time()
        r = requests.post("http://localhost:8123/", data=query_sql, auth=auth)
        query_time = time.time() - start_time
        
        if r.status_code == 200:
            result = r.text.strip()
            print(f"   {query_name}: {query_time:.4f}s")
            print(f"      Result: {result}")
            clickhouse_times.append(query_time)
        else:
            print(f"   {query_name}: FAILED - {r.status_code}")
            
    except Exception as e:
        print(f"   {query_name}: ERROR - {e}")

# Test 5: Compare with DuckDB
print("\n5. Comparing with DuckDB...")
try:
    import duckdb
    conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
    
    start_time = time.time()
    result = conn.execute("SELECT COUNT(*) FROM variants_clinical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
    duckdb_time = time.time() - start_time
    
    print(f"   DuckDB gene lookup: {duckdb_time:.4f}s ({result:,} results)")
    
    # JOIN test
    start_time = time.time()
    join_result = conn.execute("""
        SELECT cv.gene_symbol, COUNT(*) 
        FROM variants_clinical cv 
        JOIN spliceai_practical sp ON cv.gene_symbol = sp.gene_symbol 
        WHERE cv.gene_symbol = 'BRCA2' 
        GROUP BY cv.gene_symbol
    """).fetchone()
    duckdb_join_time = time.time() - start_time
    
    print(f"   DuckDB JOIN query: {duckdb_join_time:.4f}s")
    
    conn.close()
    
    # Performance comparison
    if clickhouse_times:
        avg_clickhouse = sum(clickhouse_times) / len(clickhouse_times)
        print(f"\n6. PERFORMANCE COMPARISON:")
        print(f"   ClickHouse average: {avg_clickhouse:.4f}s")
        print(f"   DuckDB simple: {duckdb_time:.4f}s")
        print(f"   DuckDB JOIN: {duckdb_join_time:.4f}s")
        
        if avg_clickhouse < duckdb_time:
            improvement = duckdb_time / avg_clickhouse
            print(f"   IMPROVEMENT: ClickHouse {improvement:.1f}x faster!")
        else:
            print(f"   ClickHouse not faster for simple queries")
            
        if avg_clickhouse < duckdb_join_time:
            join_improvement = duckdb_join_time / avg_clickhouse
            print(f"   JOIN IMPROVEMENT: ClickHouse {join_improvement:.1f}x faster for JOINs!")
    
except Exception as e:
    print(f"   DuckDB comparison error: {e}")

print(f"\n{'='*50}")
print("CLICKHOUSE LOCAL TEST COMPLETE")
print("="*50)
