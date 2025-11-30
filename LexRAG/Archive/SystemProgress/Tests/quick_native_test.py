import clickhouse_connect
import time

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

print("QUICK NATIVE VCF TEST")
print("="*30)

try:
    # Test file access
    result = client.query("SELECT * FROM file('user_files/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 1")
    print("SUCCESS: Native VCF readable!")
    print(f"Columns: {len(result.column_names)}")
    
    # Quick speed test (100K rows)
    start = time.time()
    count_result = client.query("SELECT COUNT(*) FROM (SELECT * FROM file('user_files/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 100000)")
    test_time = time.time() - start
    
    count = count_result.result_rows[0][0]
    rate = count / test_time
    
    print(f"Speed test: {count:,} rows in {test_time:.2f}s")
    print(f"Native rate: {rate:.0f} variants/sec")
    print(f"Python rate: 85,455 variants/sec")
    
    if rate > 85455:
        improvement = rate / 85455
        full_hours = 3_433_300_000 / rate / 3600
        print(f"FASTER: {improvement:.1f}x improvement!")
        print(f"Full dataset: {full_hours:.1f} hours (vs 10.8 hours)")
    else:
        print("Not faster than Python method")
        
except Exception as e:
    print(f"Native VCF test failed: {e}")
