"""
Test ClickHouse Native VCF Reader with Volume Mount
Test native file() function with mounted data directory
"""

import clickhouse_connect
import time

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def test_native_vcf_with_mount():
    """Test native VCF reader with mounted data directory"""
    log("TESTING NATIVE VCF READER WITH VOLUME MOUNT")
    log("="*60)
    
    try:
        # Connect to new ClickHouse instance
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: ClickHouse connected")
        
        # Test file access (mounted at /data)
        log("Testing file access...")
        
        # Try to read file info
        try:
            file_info = client.query("SELECT * FROM file('/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparatedWithNames') LIMIT 1")
            log("SUCCESS: File accessible via native reader")
            
            # Get column info
            columns = file_info.column_names
            log(f"Detected columns: {len(columns)}")
            log(f"Sample columns: {columns[:8]}")
            
        except Exception as e:
            log(f"File access failed: {e}")
            
            # Try alternative format
            try:
                file_info = client.query("SELECT * FROM file('/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated') LIMIT 1")
                log("SUCCESS: File accessible with TabSeparated format")
            except Exception as e2:
                log(f"Alternative format failed: {e2}")
                return False
        
        # Speed test: Native import vs Python parsing
        log("\nTesting native import speed (1M row sample)...")
        
        start_time = time.time()
        
        # Create test table with native import
        client.command("CREATE DATABASE IF NOT EXISTS speed_test")
        
        create_query = """
            CREATE TABLE speed_test.native_splice AS
            SELECT * FROM file('/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated')
            LIMIT 1000000
        """
        
        client.command(create_query)
        
        import_time = time.time() - start_time
        
        # Check results
        count = client.query("SELECT COUNT(*) FROM speed_test.native_splice").result_rows[0][0]
        
        log(f"SUCCESS: Native import complete")
        log(f"   Rows: {count:,}")
        log(f"   Time: {import_time:.2f} seconds")
        log(f"   Rate: {count/import_time:.0f} variants/second")
        
        # Compare with Python rate
        python_rate = 85455
        native_rate = count / import_time
        
        log(f"\nSPEED COMPARISON:")
        log(f"   Python parsing: {python_rate:.0f} variants/sec")
        log(f"   Native import: {native_rate:.0f} variants/sec")
        
        if native_rate > python_rate:
            improvement = native_rate / python_rate
            log(f"   IMPROVEMENT: {improvement:.1f}x faster with native!")
            
            # Calculate time for full dataset
            full_time_hours = 3_433_300_000 / native_rate / 3600
            log(f"   Full dataset time: {full_time_hours:.1f} hours")
            
            if full_time_hours < 5:
                log(f"   EXCELLENT: Full migration <5 hours")
            elif full_time_hours < 8:
                log(f"   GOOD: Full migration <8 hours")
            else:
                log(f"   LONG: Full migration {full_time_hours:.1f} hours")
        else:
            log(f"   Native not faster - Python method better")
        
        # Test data quality
        log("\nTesting data quality...")
        sample = client.query("SELECT * FROM speed_test.native_splice LIMIT 3").result_rows
        for i, row in enumerate(sample):
            log(f"   Row {i+1}: {row[:6]}...")  # Show first 6 columns
        
        # Cleanup
        client.command("DROP TABLE speed_test.native_splice")
        
        return native_rate > python_rate, native_rate
        
    except Exception as e:
        log(f"ERROR: Native VCF test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("NATIVE VCF READER TEST WITH VOLUME MOUNT")
    log("="*80)
    log("Testing if native import is faster than Python parsing")
    
    is_faster, rate = test_native_vcf_with_mount()
    
    if is_faster:
        full_hours = 3_433_300_000 / rate / 3600
        log(f"\nRESULT: Native import is faster")
        log(f"Full SpliceAI migration time: {full_hours:.1f} hours")
        log(f"READY: Can proceed with optimized full migration")
    else:
        log(f"\nRESULT: Python parsing remains best option")
        log(f"Full SpliceAI migration time: 10.8 hours")

if __name__ == "__main__":
    main()
