"""
Fix ClickHouse Native VCF Reader
Systematically solve the VCF format issues
"""

import clickhouse_connect
import time
import gzip

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def analyze_vcf_structure():
    """Analyze the actual VCF file structure"""
    log("ANALYZING VCF FILE STRUCTURE")
    log("="*50)
    
    vcf_file = "D:/LexAI3/LexRAG/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz"
    
    try:
        with gzip.open(vcf_file, 'rt') as f:
            line_count = 0
            header_lines = []
            data_lines = []
            
            for line in f:
                line_count += 1
                
                if line.startswith('#'):
                    header_lines.append(line.strip())
                    if line_count > 50:  # Limit header analysis
                        break
                else:
                    data_lines.append(line.strip())
                    if len(data_lines) >= 3:  # Get 3 data lines
                        break
        
        log(f"Header lines: {len(header_lines)}")
        log(f"Last header: {header_lines[-1] if header_lines else 'None'}")
        
        log(f"\nData line analysis:")
        for i, line in enumerate(data_lines):
            parts = line.split('\t')
            log(f"  Line {i+1}: {len(parts)} columns")
            log(f"    Sample: {parts[:5]}")
        
        # Check if all data lines have same column count
        if data_lines:
            col_counts = [len(line.split('\t')) for line in data_lines]
            if len(set(col_counts)) == 1:
                log(f"GOOD: All data lines have {col_counts[0]} columns")
                return col_counts[0], data_lines[0].split('\t')[:10]
            else:
                log(f"PROBLEM: Variable column counts: {col_counts}")
                return None, None
        
    except Exception as e:
        log(f"ERROR analyzing VCF: {e}")
        return None, None

def create_manual_schema(column_count, sample_columns):
    """Create manual schema for ClickHouse based on VCF analysis"""
    log(f"\nCREATING MANUAL SCHEMA FOR {column_count} COLUMNS")
    log("="*50)
    
    # Standard VCF columns + SpliceAI specific
    if column_count >= 8:
        schema = """
            chrom String,
            pos UInt64,
            id String,
            ref String,
            alt String,
            qual String,
            filter String,
            info String
        """
        
        # Add extra columns if present
        for i in range(8, column_count):
            schema += f",\n            col{i+1} String"
        
        log(f"Manual schema created for {column_count} columns")
        return schema.strip()
    else:
        log(f"ERROR: Too few columns ({column_count})")
        return None

def test_manual_schema_import():
    """Test import with manual schema specification"""
    log("\nTESTING MANUAL SCHEMA IMPORT")
    log("="*50)
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Analyze VCF first
        col_count, sample_cols = analyze_vcf_structure()
        if not col_count:
            log("Cannot proceed - VCF analysis failed")
            return False
        
        # Create manual schema
        schema = create_manual_schema(col_count, sample_cols)
        if not schema:
            log("Cannot proceed - schema creation failed")
            return False
        
        # Test with manual schema
        log("Testing native import with manual schema...")
        
        client.command("CREATE DATABASE IF NOT EXISTS manual_test")
        
        # Create table with manual schema
        create_table = f"""
            CREATE TABLE manual_test.splice_manual (
                {schema}
            ) ENGINE = MergeTree()
            ORDER BY (chrom, pos)
        """
        
        client.command(create_table)
        log("SUCCESS: Manual schema table created")
        
        # Test import speed
        start_time = time.time()
        
        insert_query = f"""
            INSERT INTO manual_test.splice_manual
            SELECT * FROM file('spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated', '{schema}')
            LIMIT 100000
        """
        
        client.command(insert_query)
        
        import_time = time.time() - start_time
        
        # Check results
        count = client.query("SELECT COUNT(*) FROM manual_test.splice_manual").result_rows[0][0]
        
        log(f"SUCCESS: Manual schema import complete")
        log(f"   Rows: {count:,}")
        log(f"   Time: {import_time:.2f}s")
        
        native_rate = count / import_time
        python_rate = 85455
        
        log(f"\nPERFORMANCE COMPARISON:")
        log(f"   Python: {python_rate:.0f} variants/sec")
        log(f"   Native: {native_rate:.0f} variants/sec")
        
        if native_rate > python_rate:
            improvement = native_rate / python_rate
            full_hours = 3_433_300_000 / native_rate / 3600
            log(f"   IMPROVEMENT: {improvement:.1f}x faster!")
            log(f"   Full dataset: {full_hours:.1f} hours (vs 10.8 hours)")
            
            if full_hours < 5:
                log("   EXCELLENT: <5 hours for full dataset")
            elif full_hours < 8:
                log("   GOOD: <8 hours for full dataset")
            
            return True, native_rate
        else:
            log("   Native not faster - stick with Python")
            return False, python_rate
        
    except Exception as e:
        log(f"ERROR: Manual schema test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("FIXING CLICKHOUSE NATIVE VCF READER")
    log("="*80)
    log("Goal: Get native reader working for potential speed improvement")
    log("Time limit: 3-4 hours to make it work")
    
    success, rate = test_manual_schema_import()
    
    log(f"\n{'='*80}")
    log("NATIVE VCF FIX ATTEMPT COMPLETE")
    log('='*80)
    
    if success:
        full_hours = 3_433_300_000 / rate / 3600
        log(f"SUCCESS: Native VCF reader working")
        log(f"Speed improvement achieved")
        log(f"Full migration time: {full_hours:.1f} hours")
        log("RECOMMENDATION: Use native method for full dataset")
    else:
        log(f"FAILED: Native VCF reader not working")
        log(f"FALLBACK: Use Python method (10.8 hours)")

if __name__ == "__main__":
    main()
