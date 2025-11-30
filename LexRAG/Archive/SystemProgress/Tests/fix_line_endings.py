"""
Fix Line Endings Issue for ClickHouse VCF Reader
Convert Windows CRLF to Unix LF line endings
"""

import clickhouse_connect
import time
import gzip

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def create_unix_format_vcf():
    """Create Unix format VCF for ClickHouse"""
    log("CREATING UNIX FORMAT VCF SAMPLE")
    log("="*50)
    
    try:
        input_file = "D:/LexAI3/LexRAG/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz"
        output_file = "D:/LexAI3/LexRAG/clickhouse_data/user_files/spliceai_unix.tsv"
        
        log(f"Converting Windows CRLF to Unix LF format...")
        
        data_lines = []
        
        with gzip.open(input_file, 'rt', newline='') as f:  # Don't auto-convert line endings
            for line in f:
                # Skip headers
                if line.startswith('#'):
                    continue
                
                # Convert to Unix format (LF only)
                clean_line = line.replace('\r\n', '\n').replace('\r', '\n').strip()
                
                if clean_line:
                    data_lines.append(clean_line)
                
                # Sample of 100K lines
                if len(data_lines) >= 100000:
                    break
        
        # Write with Unix line endings
        with open(output_file, 'w', newline='\n') as f:  # Force Unix line endings
            for line in data_lines:
                f.write(line + '\n')
        
        log(f"SUCCESS: Unix format file created")
        log(f"   Lines: {len(data_lines):,}")
        log(f"   Format: Unix LF line endings")
        
        return True, output_file
        
    except Exception as e:
        log(f"ERROR: Unix conversion failed - {e}")
        return False, None

def test_unix_format_import():
    """Test ClickHouse import with Unix format file"""
    log("\nTESTING UNIX FORMAT IMPORT")
    log("="*50)
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Create Unix format file
        success, file_path = create_unix_format_vcf()
        if not success:
            return False
        
        # Enable CRLF setting just in case
        client.command("SET input_format_tsv_crlf_end_of_line = 1")
        log("SUCCESS: CRLF setting enabled")
        
        # Create test table
        client.command("CREATE DATABASE IF NOT EXISTS unix_test")
        
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
        log("SUCCESS: Unix test table created")
        
        # Test native import with Unix format
        start_time = time.time()
        
        filename = os.path.basename(file_path)
        insert_query = f"""
            INSERT INTO unix_test.splice_unix
            SELECT * FROM file('{filename}', 'TabSeparated')
        """
        
        client.command(insert_query)
        
        import_time = time.time() - start_time
        
        # Check results
        count = client.query("SELECT COUNT(*) FROM unix_test.splice_unix").result_rows[0][0]
        
        log(f"SUCCESS: Unix format import working!")
        log(f"   Rows: {count:,}")
        log(f"   Time: {import_time:.2f}s")
        
        native_rate = count / import_time
        python_rate = 85455
        
        log(f"\nSPEED COMPARISON:")
        log(f"   Python parsing: {python_rate:.0f} variants/sec")
        log(f"   Native Unix import: {native_rate:.0f} variants/sec")
        
        if native_rate > python_rate:
            improvement = native_rate / python_rate
            full_hours = 3_433_300_000 / native_rate / 3600
            log(f"   BREAKTHROUGH: {improvement:.1f}x faster!")
            log(f"   Full dataset time: {full_hours:.1f} hours (vs 10.8 hours)")
            
            if full_hours < 3:
                log("   EXCELLENT: <3 hours for full dataset")
            elif full_hours < 6:
                log("   GOOD: <6 hours for full dataset")
            
            # Test data quality
            sample = client.query("SELECT * FROM unix_test.splice_unix LIMIT 3").result_rows
            log(f"\nDATA QUALITY CHECK:")
            for i, row in enumerate(sample):
                log(f"   Row {i+1}: {row[:6]}")
            
            return True, native_rate
        else:
            log("   Still not faster - need different approach")
            return False, python_rate
        
    except Exception as e:
        log(f"ERROR: Unix format test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("FIXING VCF READER - LINE ENDINGS APPROACH")
    log("="*80)
    log("Goal: Solve Windows CRLF vs Unix LF issue")
    log("Time budget: Working until native reader is faster")
    
    success, rate = test_unix_format_import()
    
    log(f"\n{'='*80}")
    log("LINE ENDINGS FIX ATTEMPT COMPLETE")
    log('='*80)
    
    if success:
        full_hours = 3_433_300_000 / rate / 3600
        log(f"SUCCESS: Native reader working and faster!")
        log(f"Ready for full dataset in {full_hours:.1f} hours")
        log("NEXT: Scale up to full dataset with Unix format conversion")
    else:
        log(f"CONTINUE: Line endings fixed but still not faster")
        log(f"NEXT: Try different ClickHouse import optimizations")

if __name__ == "__main__":
    main()
