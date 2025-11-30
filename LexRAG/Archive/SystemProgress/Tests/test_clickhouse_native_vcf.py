"""
Test ClickHouse Native VCF Reader
Test if native file() function is faster than Python parsing
"""

import clickhouse_connect
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def test_native_vcf_reader():
    """Test ClickHouse native VCF reading performance"""
    log("TESTING CLICKHOUSE NATIVE VCF READER")
    log("="*60)
    log("Goal: Test if native file() function is faster than Python parsing")
    
    try:
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: ClickHouse connected")
        
        # Create separate test database (don't affect existing data)
        client.command("CREATE DATABASE IF NOT EXISTS native_test")
        log("SUCCESS: Native test database created")
        
        # Check SpliceAI file
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        if not vcf_file.exists():
            log(f"ERROR: SpliceAI VCF not found: {vcf_file}")
            return False
        
        file_size_gb = vcf_file.stat().st_size / (1024*1024*1024)
        log(f"SUCCESS: SpliceAI VCF found ({file_size_gb:.1f} GB)")
        
        # Test 1: Check VCF file format first
        log("Testing VCF file format detection...")
        try:
            # Try to read just the schema
            schema_query = f"DESCRIBE file('{vcf_file}', 'TabSeparatedWithNames')"
            schema_result = client.query(schema_query)
            log(f"SUCCESS: VCF schema detected with {len(schema_result.result_rows)} columns")
            
            # Show detected columns
            for i, (col_name, col_type) in enumerate(schema_result.result_rows[:10]):
                log(f"   Column {i+1}: {col_name} ({col_type})")
                
        except Exception as e:
            log(f"Schema detection failed: {e}")
            log("Trying alternative format...")
            
            try:
                schema_query = f"DESCRIBE file('{vcf_file}', 'TabSeparated')"
                schema_result = client.query(schema_query)
                log(f"SUCCESS: Alternative format detected")
            except Exception as e2:
                log(f"Both formats failed: {e2}")
                return False
        
        # Test 2: Native import speed test (small sample)
        log("\nTesting native import speed (1 million rows sample)...")
        
        start_time = time.time()
        
        # Create test table with native import (LIMIT for speed test)
        create_and_import = f"""
            CREATE TABLE native_test.splice_speed_test AS
            SELECT * FROM file('{vcf_file}', 'TabSeparatedWithNames')
            LIMIT 1000000
        """
        
        client.command(create_and_import)
        
        import_time = time.time() - start_time
        
        # Check results
        test_count = client.query("SELECT COUNT(*) FROM native_test.splice_speed_test").result_rows[0][0]
        
        log(f"SUCCESS: Native import test complete")
        log(f"   Rows imported: {test_count:,}")
        log(f"   Import time: {import_time:.2f} seconds")
        log(f"   Native rate: {test_count/import_time:.0f} variants/second")
        
        # Compare with our Python parsing rate
        python_rate = 85455  # From previous test
        native_rate = test_count/import_time
        
        log(f"\nPERFORMANCE COMPARISON:")
        log(f"   Python parsing: {python_rate:.0f} variants/sec")
        log(f"   Native import: {native_rate:.0f} variants/sec")
        
        if native_rate > python_rate:
            improvement = native_rate / python_rate
            log(f"   IMPROVEMENT: Native is {improvement:.1f}x faster!")
            
            # Calculate new time estimate for full dataset
            full_time_hours = 3_433_300_000 / native_rate / 3600
            log(f"   Full dataset time: {full_time_hours:.1f} hours (vs {3_433_300_000 / python_rate / 3600:.1f} hours)")
            
        else:
            log(f"   Native is slower - stick with Python parsing")
        
        # Test 3: Check data quality
        log("\nTesting imported data quality...")
        
        # Check if we have gene symbols
        genes_with_data = client.query("SELECT COUNT(DISTINCT gene_symbol) FROM native_test.splice_speed_test WHERE gene_symbol != ''").result_rows[0][0]
        log(f"   Genes with data: {genes_with_data:,}")
        
        # Check for test genes
        test_genes = ['BRCA1', 'BRCA2', 'TP53', 'CFTR']
        for gene in test_genes:
            gene_count = client.query(f"SELECT COUNT(*) FROM native_test.splice_speed_test WHERE gene_symbol = '{gene}'").result_rows[0][0]
            log(f"   {gene}: {gene_count:,} variants")
        
        # Cleanup test table
        client.command("DROP TABLE native_test.splice_speed_test")
        log("Cleanup: Test table removed")
        
        return native_rate > python_rate, native_rate
        
    except Exception as e:
        log(f"ERROR: Native VCF test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("CLICKHOUSE NATIVE VCF READER TEST")
    log("="*80)
    log("Time estimate: 5-10 minutes for speed comparison")
    log("Will NOT run full migration without permission")
    
    is_faster, native_rate = test_native_vcf_reader()
    
    log(f"\n{'='*80}")
    log("NATIVE VCF TEST COMPLETE")
    log('='*80)
    
    if is_faster:
        full_time_hours = 3_433_300_000 / native_rate / 3600
        log(f"RESULT: Native import is faster")
        log(f"Full dataset time: {full_time_hours:.1f} hours")
        log(f"RECOMMENDATION: Use native import for full migration")
    else:
        log(f"RESULT: Python parsing is faster")
        log(f"RECOMMENDATION: Continue with current method")

if __name__ == "__main__":
    main()
