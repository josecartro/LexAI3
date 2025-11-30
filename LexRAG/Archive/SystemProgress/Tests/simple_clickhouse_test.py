import time
import requests

print("CLICKHOUSE PERFORMANCE TEST")
print("="*40)

# Test 1: Connection
print("\n1. Testing ClickHouse connection...")
try:
    r = requests.get("http://localhost:8123/")
    if r.status_code == 200:
        print("   SUCCESS: ClickHouse responding")
    else:
        print(f"   FAILED: HTTP {r.status_code}")
        exit()
except Exception as e:
    print(f"   ERROR: {e}")
    exit()

# Test 2: Create database
print("\n2. Creating test database...")
try:
    r = requests.post("http://localhost:8123/", data="CREATE DATABASE IF NOT EXISTS genomics_test")
    if r.status_code == 200:
        print("   SUCCESS: Database created")
    else:
        print(f"   FAILED: {r.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Create table
print("\n3. Creating variants table...")
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
    r = requests.post("http://localhost:8123/", data=create_table)
    if r.status_code == 200:
        print("   SUCCESS: Table created")
    else:
        print(f"   FAILED: {r.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Insert test data
print("\n4. Inserting test data...")
test_data = [
    ("rs7412", "APOE", "Pathogenic", 0.95),
    ("rs429358", "APOE", "Risk_factor", 0.85),
    ("rs80357713", "BRCA1", "Pathogenic", 0.99),
    ("rs80357906", "BRCA2", "Pathogenic", 0.98)
]

for rsid, gene, significance, score in test_data:
    insert_sql = f"INSERT INTO genomics_test.variants VALUES ('{rsid}', '{gene}', '{significance}', {score})"
    try:
        r = requests.post("http://localhost:8123/", data=insert_sql)
        if r.status_code == 200:
            print(f"   SUCCESS: {rsid} inserted")
        else:
            print(f"   FAILED: {rsid} - {r.status_code}")
    except Exception as e:
        print(f"   ERROR: {rsid} - {e}")

# Test 5: Query performance
print("\n5. Testing query performance...")

queries = [
    ("Count all variants", "SELECT COUNT(*) FROM genomics_test.variants"),
    ("Gene lookup", "SELECT * FROM genomics_test.variants WHERE gene_symbol = 'BRCA2'"),
    ("Pathogenic variants", "SELECT gene_symbol, COUNT(*) FROM genomics_test.variants WHERE clinical_significance = 'Pathogenic' GROUP BY gene_symbol")
]

for query_name, query_sql in queries:
    try:
        start_time = time.time()
        r = requests.post("http://localhost:8123/", data=query_sql)
        query_time = time.time() - start_time
        
        if r.status_code == 200:
            result = r.text.strip()
            print(f"   {query_name}: {query_time:.4f}s - Result: {result}")
        else:
            print(f"   {query_name}: FAILED - HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   {query_name}: ERROR - {e}")

print("\n6. Comparing with DuckDB...")
try:
    import duckdb
    conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
    
    start_time = time.time()
    result = conn.execute("SELECT COUNT(*) FROM variants_clinical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
    duckdb_time = time.time() - start_time
    
    print(f"   DuckDB same query: {duckdb_time:.4f}s ({result:,} results)")
    
    conn.close()
    
except Exception as e:
    print(f"   DuckDB comparison error: {e}")

print(f"\n{'='*40}")
print("CLICKHOUSE TEST COMPLETE")
print("Compare query times to assess improvement")
print("="*40)
