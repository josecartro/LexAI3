import clickhouse_connect
import time

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

print("FINAL NATIVE IMPORT TEST")
print("="*40)

try:
    # Clean setup
    client.command("DROP TABLE IF EXISTS unix_test.splice_unix")
    client.command("SET input_format_tsv_crlf_end_of_line = 1")
    
    # Create table
    client.command("""
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
    """)
    
    print("Table created")
    
    # Test import
    start = time.time()
    client.command("INSERT INTO unix_test.splice_unix SELECT * FROM file('spliceai_headerless_sample.tsv', 'TabSeparated')")
    import_time = time.time() - start
    
    # Check results
    count = client.query("SELECT COUNT(*) FROM unix_test.splice_unix").result_rows[0][0]
    
    print(f"NATIVE IMPORT RESULT:")
    print(f"   Rows: {count:,}")
    print(f"   Time: {import_time:.2f}s")
    
    if count > 0:
        native_rate = count / import_time
        print(f"   Rate: {native_rate:.0f} variants/sec")
        
        if native_rate > 85455:
            improvement = native_rate / 85455
            full_hours = 3_433_300_000 / native_rate / 3600
            print(f"   SUCCESS: {improvement:.1f}x faster!")
            print(f"   Full dataset: {full_hours:.1f} hours")
        else:
            print(f"   Not faster than Python (85,455/sec)")
            
        # Sample data
        sample = client.query("SELECT chrom, pos, variant_id FROM unix_test.splice_unix LIMIT 2").result_rows
        print(f"Sample data:")
        for row in sample:
            print(f"   {row}")
    else:
        print("   FAILED: No data imported")
        
except Exception as e:
    print(f"ERROR: {e}")

print("Native test complete")
