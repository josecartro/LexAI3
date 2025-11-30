"""
Solve VCF Header Issue for ClickHouse Native Reader
Focus on making the native reader work properly
"""

import clickhouse_connect
import time
import gzip
import tempfile
import os

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def create_headerless_vcf_sample():
    """Create a headerless VCF sample for ClickHouse testing"""
    log("CREATING HEADERLESS VCF SAMPLE")
    log("="*50)
    
    try:
        input_file = "D:/LexAI3/LexRAG/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz"
        output_file = "D:/LexAI3/LexRAG/clickhouse_data/user_files/spliceai_headerless_sample.tsv"
        
        log(f"Input: {input_file}")
        log(f"Output: {output_file}")
        
        data_lines = []
        
        with gzip.open(input_file, 'rt') as f:
            for line in f:
                # Skip header lines
                if line.startswith('#'):
                    continue
                
                # Process data lines
                line = line.strip()
                if line:
                    data_lines.append(line)
                
                # Create sample with first 100K lines
                if len(data_lines) >= 100000:
                    break
        
        # Write headerless TSV
        with open(output_file, 'w') as f:
            for line in data_lines:
                f.write(line + '\n')
        
        log(f"SUCCESS: Created headerless sample")
        log(f"   Lines: {len(data_lines):,}")
        log(f"   File: {output_file}")
        
        # Analyze first line for schema
        first_parts = data_lines[0].split('\t')
        log(f"   Columns: {len(first_parts)}")
        log(f"   Sample: {first_parts[:5]}")
        
        return True, len(first_parts), output_file
        
    except Exception as e:
        log(f"ERROR creating headerless VCF: {e}")
        return False, 0, None

def test_headerless_import():
    """Test ClickHouse import with headerless file"""
    log("\nTESTING HEADERLESS IMPORT")
    log("="*50)
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Create headerless sample
        success, col_count, file_path = create_headerless_vcf_sample()
        if not success:
            return False
        
        # Create table with proper schema
        client.command("CREATE DATABASE IF NOT EXISTS headerless_test")
        
        create_table = """
            CREATE TABLE headerless_test.splice_clean (
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
        log("SUCCESS: Clean schema table created")
        
        # Test native import speed
        start_time = time.time()
        
        # Use relative path from user_files
        filename = os.path.basename(file_path)
        insert_query = f"""
            INSERT INTO headerless_test.splice_clean
            SELECT * FROM file('{filename}', 'TabSeparated')
        """
        
        client.command(insert_query)
        
        import_time = time.time() - start_time
        
        # Check results
        count = client.query("SELECT COUNT(*) FROM headerless_test.splice_clean").result_rows[0][0]
        
        log(f"SUCCESS: Headerless native import working!")
        log(f"   Rows: {count:,}")
        log(f"   Time: {import_time:.2f}s")
        
        native_rate = count / import_time
        python_rate = 85455
        
        log(f"\nSPEED COMPARISON:")
        log(f"   Python parsing: {python_rate:.0f} variants/sec")
        log(f"   Native import: {native_rate:.0f} variants/sec")
        
        if native_rate > python_rate:
            improvement = native_rate / python_rate
            full_hours = 3_433_300_000 / native_rate / 3600
            log(f"   BREAKTHROUGH: {improvement:.1f}x faster!")
            log(f"   Full dataset time: {full_hours:.1f} hours")
            
            return True, native_rate
        else:
            log("   Not faster than Python")
            return False, python_rate
        
    except Exception as e:
        log(f"ERROR: Headerless test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("SOLVING VCF HEADER ISSUE FOR NATIVE READER")
    log("="*80)
    log("Approach: Create headerless VCF for ClickHouse native import")
    log("Goal: Make native reader work faster than Python parsing")
    
    success, rate = test_headerless_import()
    
    if success:
        full_hours = 3_433_300_000 / rate / 3600
        log(f"\nSUCCESS: Native VCF reader working!")
        log(f"Ready to process full dataset in {full_hours:.1f} hours")
    else:
        log(f"\nNative reader still not working - continue debugging")

if __name__ == "__main__":
    main()
