import clickhouse_connect
import time

print("TESTING DIFFERENT FILE FORMATS")
print("="*50)

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

# Create test database
client.command("CREATE DATABASE IF NOT EXISTS format_test")

formats_to_try = [
    ("CSV", "CSV"),
    ("TSV", "TSV"), 
    ("TabSeparated", "TabSeparated"),
    ("TabSeparatedRaw", "TabSeparatedRaw")
]

for format_name, format_code in formats_to_try:
    print(f"\nTesting {format_name} format...")
    
    try:
        # Drop and recreate table
        client.command("DROP TABLE IF EXISTS format_test.splice_test")
        
        client.command("""
            CREATE TABLE format_test.splice_test (
                chrom String,
                pos String,
                variant_id String,
                ref String,
                alt String,
                qual String,
                filter String,
                info String
            ) ENGINE = MergeTree()
            ORDER BY chrom
        """)
        
        # Set relaxed parsing
        client.command("SET input_format_tsv_crlf_end_of_line = 1")
        client.command("SET input_format_tsv_allow_variable_number_of_columns = 1")
        client.command("SET input_format_skip_unknown_fields = 1")
        
        # Test import
        start = time.time()
        insert_cmd = f"INSERT INTO format_test.splice_test SELECT * FROM file('spliceai_headerless_sample.tsv', '{format_code}')"
        client.command(insert_cmd)
        import_time = time.time() - start
        
        # Check results
        count = client.query("SELECT COUNT(*) FROM format_test.splice_test").result_rows[0][0]
        
        if count > 0:
            rate = count / import_time
            print(f"   SUCCESS: {count:,} rows in {import_time:.2f}s")
            print(f"   Rate: {rate:.0f} variants/sec")
            
            if rate > 85455:
                improvement = rate / 85455
                full_hours = 3_433_300_000 / rate / 3600
                print(f"   BREAKTHROUGH: {improvement:.1f}x faster!")
                print(f"   Full dataset: {full_hours:.1f} hours")
                
                # Test data quality
                sample = client.query("SELECT chrom, pos, variant_id FROM format_test.splice_test LIMIT 2").result_rows
                print(f"   Sample data: {sample}")
                
                print(f"   FORMAT {format_name} WORKS!")
                break
            else:
                print(f"   Not faster than Python")
        else:
            print(f"   FAILED: No data imported")
            
    except Exception as e:
        print(f"   ERROR: {str(e)[:100]}")

print("\nFormat testing complete")
