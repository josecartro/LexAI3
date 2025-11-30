import clickhouse_connect
import time

print("TESTING UNIX FORMAT IMPORT")
print("="*40)

try:
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    
    # Enable CRLF setting
    client.command("SET input_format_tsv_crlf_end_of_line = 1")
    
    # Create database
    client.command("CREATE DATABASE IF NOT EXISTS unix_test")
    
    # Create table
    create_table = """
        CREATE TABLE unix_test.splice_unix (
            chrom String,
            pos UInt64,
            variant_id String,
            ref String,
            alt String,
            qual String,
            filter String,
            info String
        ) ENGINE = MergeTree()
        ORDER BY (chrom, pos)
    """
    
    client.command(create_table)
    print("SUCCESS: Table created")
    
    # Test import
    start_time = time.time()
    
    insert_query = """
        INSERT INTO unix_test.splice_unix
        SELECT * FROM file('spliceai_headerless_sample.tsv', 'TabSeparated')
    """
    
    client.command(insert_query)
    
    import_time = time.time() - start_time
    
    # Check results
    count = client.query("SELECT COUNT(*) FROM unix_test.splice_unix").result_rows[0][0]
    
    print(f"SUCCESS: Native import working!")
    print(f"   Rows: {count:,}")
    print(f"   Time: {import_time:.2f}s")
    
    native_rate = count / import_time
    python_rate = 85455
    
    print(f"\nSPEED COMPARISON:")
    print(f"   Python: {python_rate:.0f} variants/sec")
    print(f"   Native: {native_rate:.0f} variants/sec")
    
    if native_rate > python_rate:
        improvement = native_rate / python_rate
        full_hours = 3_433_300_000 / native_rate / 3600
        print(f"   BREAKTHROUGH: {improvement:.1f}x faster!")
        print(f"   Full dataset: {full_hours:.1f} hours")
    else:
        print("   Need more optimization")
    
    # Test data quality
    sample = client.query("SELECT * FROM unix_test.splice_unix LIMIT 2").result_rows
    print(f"\nData sample:")
    for row in sample:
        print(f"   {row}")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\nNative import test complete")
