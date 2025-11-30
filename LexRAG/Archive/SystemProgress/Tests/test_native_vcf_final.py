import clickhouse_connect
import time

print("TESTING NATIVE VCF READER WITH SHARED STORAGE")
print("="*60)

try:
    # Connect
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    print("SUCCESS: ClickHouse connected")
    
    # Test file access
    print("\nTesting file access...")
    try:
        # Test if file is accessible
        test_query = "SELECT * FROM file('user_files/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 1"
        result = client.query(test_query)
        print("SUCCESS: Native VCF file accessible!")
        
        # Show what we got
        print(f"Columns detected: {len(result.column_names)}")
        print(f"Sample data: {result.result_rows[0][:5]}...")
        
    except Exception as e:
        print(f"File access failed: {e}")
        return False
    
    # Speed test: Native import
    print("\nTesting native import speed (1M rows)...")
    
    start_time = time.time()
    
    # Create database and table with native import
    client.command("CREATE DATABASE IF NOT EXISTS native_test")
    
    create_native = """
        CREATE TABLE native_test.splice_native AS
        SELECT * FROM file('user_files/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated')
        LIMIT 1000000
    """
    
    client.command(create_native)
    
    import_time = time.time() - start_time
    
    # Check results
    count = client.query("SELECT COUNT(*) FROM native_test.splice_native").result_rows[0][0]
    
    print(f"SUCCESS: Native import complete")
    print(f"   Rows: {count:,}")
    print(f"   Time: {import_time:.2f} seconds")
    
    native_rate = count / import_time
    python_rate = 85455
    
    print(f"\nSPEED COMPARISON:")
    print(f"   Python parsing: {python_rate:.0f} variants/sec")
    print(f"   Native import: {native_rate:.0f} variants/sec")
    
    if native_rate > python_rate:
        improvement = native_rate / python_rate
        print(f"   IMPROVEMENT: {improvement:.1f}x faster!")
        
        # Calculate new time for full dataset
        full_hours = 3_433_300_000 / native_rate / 3600
        print(f"   Full dataset time: {full_hours:.1f} hours")
        
        if full_hours < 5:
            print("   EXCELLENT: Full migration <5 hours")
            print("   RECOMMENDATION: Use native method")
        elif full_hours < 8:
            print("   GOOD: Full migration <8 hours")
            print("   RECOMMENDATION: Use native method")
        else:
            print(f"   STILL LONG: {full_hours:.1f} hours")
    else:
        print("   Native not faster - Python method better")
    
    # Cleanup test
    client.command("DROP TABLE native_test.splice_native")
    
    return True
    
except Exception as e:
    print(f"ERROR: {e}")
    return False

if __name__ == "__main__":
    success = test_native_vcf_final()
    if success:
        print("\nNATIVE VCF TEST COMPLETE")
    else:
        print("\nNATIVE VCF TEST FAILED")
