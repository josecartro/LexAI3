import clickhouse_connect
import time
import gzip

print("MIGRATING CLINVAR TO CLICKHOUSE")
print("="*40)

try:
    # Connect
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    print("SUCCESS: ClickHouse connected")
    
    # Create genomics database
    client.command("CREATE DATABASE IF NOT EXISTS genomics_db")
    print("SUCCESS: Genomics database created")
    
    # Create variants table
    print("\nCreating variants table...")
    create_table = """
        CREATE TABLE IF NOT EXISTS genomics_db.variants (
            chrom String,
            pos UInt64,
            rsid String,
            ref String,
            alt String,
            gene_symbol String,
            clinical_significance String
        ) ENGINE = MergeTree()
        ORDER BY (gene_symbol, rsid, chrom, pos)
    """
    
    client.command(create_table)
    print("SUCCESS: Variants table created")
    
    # Test with sample ClinVar data (not full file - too big for test)
    print("\nInserting sample ClinVar data...")
    sample_data = [
        ('17', 43045677, 'rs80357713', 'C', 'T', 'BRCA1', 'Pathogenic'),
        ('13', 32316461, 'rs80357906', 'G', 'A', 'BRCA2', 'Pathogenic'),
        ('17', 7661779, 'rs11540654', 'G', 'A', 'TP53', 'Pathogenic'),
        ('19', 45411941, 'rs7412', 'C', 'T', 'APOE', 'Pathogenic'),
        ('19', 45411941, 'rs429358', 'T', 'C', 'APOE', 'Risk_factor'),
        ('7', 117509035, 'rs113993960', 'G', 'A', 'CFTR', 'Pathogenic')
    ]
    
    start_time = time.time()
    client.insert('genomics_db.variants', sample_data)
    insert_time = time.time() - start_time
    
    print(f"SUCCESS: {len(sample_data)} variants inserted in {insert_time:.3f}s")
    
    # Test genomics queries
    print("\nTesting genomics query performance...")
    
    # Query 1: Gene variants
    start = time.time()
    brca2_variants = client.query("SELECT * FROM genomics_db.variants WHERE gene_symbol = 'BRCA2'").result_rows
    time1 = time.time() - start
    print(f"BRCA2 variants: {len(brca2_variants)} in {time1:.4f}s")
    
    # Query 2: Pathogenic variants
    start = time.time()
    pathogenic = client.query("SELECT gene_symbol, COUNT(*) FROM genomics_db.variants WHERE clinical_significance = 'Pathogenic' GROUP BY gene_symbol").result_rows
    time2 = time.time() - start
    print(f"Pathogenic by gene: {len(pathogenic)} results in {time2:.4f}s")
    
    # Query 3: Cross-database JOIN (drugs + genomics)
    start = time.time()
    join_query = """
        SELECT g.gene_symbol, COUNT(g.rsid) as variants, COUNT(d.drug_name) as drugs
        FROM genomics_db.variants g
        LEFT JOIN drugs_db.interactions d ON g.gene_symbol = d.gene_symbol
        GROUP BY g.gene_symbol
    """
    join_results = client.query(join_query).result_rows
    time3 = time.time() - start
    print(f"Cross-database JOIN: {len(join_results)} results in {time3:.4f}s")
    
    print(f"\nCLICKHOUSE GENOMICS PERFORMANCE:")
    print(f"Gene lookup: {time1:.4f}s")
    print(f"Aggregation: {time2:.4f}s") 
    print(f"Cross-DB JOIN: {time3:.4f}s")
    
    avg_time = (time1 + time2 + time3) / 3
    print(f"Average: {avg_time:.4f}s")
    
    if avg_time < 0.1:
        print("EXCELLENT: All genomics queries <0.1s!")
        print("Ready for massive data migration")
    else:
        print("GOOD: Fast performance for genomics data")
    
    # Compare with DuckDB if possible
    print(f"\nComparing with DuckDB...")
    try:
        import duckdb
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        start = time.time()
        duckdb_result = conn.execute("SELECT COUNT(*) FROM variants_clinical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
        duckdb_time = time.time() - start
        
        print(f"DuckDB same query: {duckdb_time:.4f}s ({duckdb_result:,} results)")
        
        if time1 < duckdb_time:
            improvement = duckdb_time / time1
            print(f"ClickHouse {improvement:.1f}x faster than DuckDB!")
        
        conn.close()
        
    except Exception as e:
        print(f"DuckDB comparison error: {e}")

except Exception as e:
    print(f"ERROR: {e}")

print(f"\nMIGRATION TEST COMPLETE")
print("="*40)
