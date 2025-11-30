import clickhouse_connect
import time

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

print("TESTING NATIVE VCF ACCESS")

try:
    # Test file access with correct path
    result = client.query("SELECT * FROM file('spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 1")
    print("SUCCESS: Native VCF accessible!")
    
    # Speed test
    start = time.time()
    count = client.query("SELECT COUNT(*) FROM (SELECT * FROM file('spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 100000)").result_rows[0][0]
    test_time = time.time() - start
    
    native_rate = count / test_time
    print(f"Native: {native_rate:.0f} variants/sec")
    print(f"Python: 85,455 variants/sec")
    
    if native_rate > 85455:
        improvement = native_rate / 85455
        full_hours = 3_433_300_000 / native_rate / 3600
        print(f"FASTER: {improvement:.1f}x improvement!")
        print(f"Full dataset: {full_hours:.1f} hours")
    else:
        print("Python method still better")
        
except Exception as e:
    print(f"Failed: {e}")
