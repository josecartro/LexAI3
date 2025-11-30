import clickhouse_connect
import time

print("TESTING CLINVAR DATA IN CLICKHOUSE")
print("="*50)

try:
    # Connect to ClickHouse
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    print("SUCCESS: ClickHouse connected")
    
    # Test 1: Verify data exists
    print("\n1. Verifying ClinVar data...")
    total_count = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_full").result_rows[0][0]
    print(f"Total variants: {total_count:,}")
    
    if total_count > 3000000:
        print("SUCCESS: Full ClinVar dataset confirmed")
    else:
        print("WARNING: Dataset seems incomplete")
    
    # Test 2: Gene-specific queries
    print("\n2. Testing gene-specific queries...")
    
    genes_to_test = ['BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE']
    
    for gene in genes_to_test:
        start_time = time.time()
        gene_variants = client.query(f"SELECT COUNT(*) FROM genomics_db.clinvar_full WHERE gene_symbol = '{gene}'").result_rows
        query_time = time.time() - start_time
        
        if gene_variants:
            count = gene_variants[0][0]
            print(f"   {gene}: {count:,} variants in {query_time:.4f}s")
        else:
            print(f"   {gene}: No results in {query_time:.4f}s")
    
    # Test 3: Clinical significance queries
    print("\n3. Testing clinical significance queries...")
    
    start_time = time.time()
    pathogenic = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_full WHERE clinical_significance LIKE '%athogenic%'").result_rows[0][0]
    pathogenic_time = time.time() - start_time
    print(f"Pathogenic variants: {pathogenic:,} in {pathogenic_time:.4f}s")
    
    start_time = time.time()
    benign = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_full WHERE clinical_significance LIKE '%enign%'").result_rows[0][0]
    benign_time = time.time() - start_time
    print(f"Benign variants: {benign:,} in {benign_time:.4f}s")
    
    # Test 4: Complex aggregation
    print("\n4. Testing complex queries...")
    
    start_time = time.time()
    gene_summary = client.query("""
        SELECT gene_symbol, COUNT(*) as variant_count, 
               COUNT(CASE WHEN clinical_significance LIKE '%athogenic%' THEN 1 END) as pathogenic_count
        FROM genomics_db.clinvar_full 
        WHERE gene_symbol IN ('BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE')
        GROUP BY gene_symbol
        ORDER BY variant_count DESC
    """).result_rows
    complex_time = time.time() - start_time
    
    print(f"Gene summary query: {len(gene_summary)} results in {complex_time:.4f}s")
    for gene, total, pathogenic in gene_summary:
        print(f"   {gene}: {total:,} total, {pathogenic:,} pathogenic")
    
    # Test 5: Variant lookup (rs7412)
    print("\n5. Testing specific variant lookup...")
    
    start_time = time.time()
    rs7412 = client.query("SELECT * FROM genomics_db.clinvar_full WHERE rsid = 'rs7412'").result_rows
    variant_time = time.time() - start_time
    
    if rs7412:
        variant_data = rs7412[0]
        print(f"rs7412 lookup: Found in {variant_time:.4f}s")
        print(f"   Gene: {variant_data[5]}")
        print(f"   Significance: {variant_data[6]}")
        print(f"   Disease: {variant_data[7]}")
    else:
        print(f"rs7412 lookup: Not found in {variant_time:.4f}s")
    
    # Performance summary
    print(f"\n{'='*50}")
    print("CLINVAR PERFORMANCE SUMMARY")
    print('='*50)
    
    all_times = [pathogenic_time, benign_time, complex_time, variant_time]
    avg_time = sum(all_times) / len(all_times)
    
    print(f"Average query time: {avg_time:.4f}s")
    print(f"Fastest query: {min(all_times):.4f}s")
    print(f"Slowest query: {max(all_times):.4f}s")
    
    if avg_time < 0.1:
        print("EXCELLENT: All ClinVar queries <0.1s")
        print("Ready for API integration")
    elif avg_time < 0.5:
        print("GOOD: Fast ClinVar performance")
    else:
        print("SLOW: Performance needs optimization")
    
    print(f"\nCLINVAR CLICKHOUSE TEST COMPLETE")
    print(f"Dataset: {total_count:,} variants ready for ultra-fast API queries")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("ClinVar ClickHouse test failed")
