"""
VCF to CSV Converter for ClickHouse Optimized Import
Convert SpliceAI VCF to CSV format for fast ClickHouse import
"""

import gzip
import csv
import time

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def convert_vcf_to_csv_sample():
    """Convert VCF sample to CSV for ClickHouse testing"""
    log("CONVERTING VCF TO CSV FOR CLICKHOUSE")
    log("="*60)
    
    try:
        input_file = "D:/LexAI3/LexRAG/data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz"
        output_file = "D:/LexAI3/LexRAG/clickhouse_data/user_files/spliceai_sample.csv"
        
        log(f"Input VCF: {input_file}")
        log(f"Output CSV: {output_file}")
        log("Converting first 100K variants to CSV format...")
        
        csv_rows = []
        header_written = False
        
        with gzip.open(input_file, 'rt') as f:
            for line_num, line in enumerate(f, 1):
                # Skip VCF headers
                if line.startswith('#'):
                    continue
                
                # Process data lines
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    pos = parts[1]
                    variant_id = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    qual = parts[5]
                    filter_val = parts[6]
                    info = parts[7]
                    
                    # Parse SpliceAI scores from INFO field
                    gene_symbol = ""
                    acceptor_gain = "0"
                    acceptor_loss = "0"
                    donor_gain = "0"
                    donor_loss = "0"
                    
                    # Extract gene symbol
                    if "SYMBOL=" in info:
                        try:
                            gene_symbol = info.split("SYMBOL=")[1].split(";")[0]
                        except:
                            gene_symbol = "unknown"
                    
                    # Extract SpliceAI scores
                    if "SpliceAI=" in info:
                        try:
                            splice_part = info.split("SpliceAI=")[1].split(";")[0]
                            scores = splice_part.split("|")
                            if len(scores) >= 4:
                                acceptor_gain = scores[0] if scores[0] != '.' else "0"
                                acceptor_loss = scores[1] if scores[1] != '.' else "0"
                                donor_gain = scores[2] if scores[2] != '.' else "0"
                                donor_loss = scores[3] if scores[3] != '.' else "0"
                        except:
                            pass
                    
                    # Create CSV row
                    csv_row = [
                        chrom, pos, variant_id, ref, alt, gene_symbol,
                        acceptor_gain, acceptor_loss, donor_gain, donor_loss
                    ]
                    
                    csv_rows.append(csv_row)
                
                # Process 100K sample
                if len(csv_rows) >= 100000:
                    log(f"Processed {len(csv_rows):,} variants for CSV conversion")
                    break
                
                if line_num % 50000 == 0:
                    log(f"   Processing line {line_num:,}...")
        
        # Write CSV file
        log("Writing CSV file...")
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'chrom', 'pos', 'variant_id', 'ref', 'alt', 'gene_symbol',
                'acceptor_gain', 'acceptor_loss', 'donor_gain', 'donor_loss'
            ])
            
            # Write data
            writer.writerows(csv_rows)
        
        log(f"SUCCESS: CSV conversion complete")
        log(f"   Rows: {len(csv_rows):,}")
        log(f"   Output: {output_file}")
        
        return True, output_file, len(csv_rows)
        
    except Exception as e:
        log(f"ERROR: CSV conversion failed - {e}")
        return False, None, 0

def test_csv_import_speed():
    """Test ClickHouse CSV import speed"""
    log("\nTESTING CLICKHOUSE CSV IMPORT SPEED")
    log("="*60)
    
    try:
        import clickhouse_connect
        
        # Connect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Convert to CSV first
        success, csv_file, row_count = convert_vcf_to_csv_sample()
        if not success:
            return False
        
        # Create database and table
        client.command("CREATE DATABASE IF NOT EXISTS csv_test")
        client.command("DROP TABLE IF EXISTS csv_test.splice_csv")
        
        create_table = """
            CREATE TABLE csv_test.splice_csv (
                chrom String,
                pos UInt64,
                variant_id String,
                ref String,
                alt String,
                gene_symbol String,
                acceptor_gain Float32,
                acceptor_loss Float32,
                donor_gain Float32,
                donor_loss Float32
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, chrom, pos)
        """
        
        client.command(create_table)
        log("SUCCESS: CSV test table created")
        
        # Test CSV import speed
        log("Testing CSV import speed...")
        start_time = time.time()
        
        # Use ClickHouse's recommended CSV import
        filename = csv_file.split('/')[-1]  # Get just filename
        insert_query = f"""
            INSERT INTO csv_test.splice_csv
            SELECT * FROM file('{filename}', 'CSVWithNames')
        """
        
        client.command(insert_query)
        
        import_time = time.time() - start_time
        
        # Verify results
        count = client.query("SELECT COUNT(*) FROM csv_test.splice_csv").result_rows[0][0]
        
        log(f"SUCCESS: CSV import complete!")
        log(f"   Rows imported: {count:,}")
        log(f"   Import time: {import_time:.2f}s")
        
        csv_rate = count / import_time
        python_rate = 85455
        
        log(f"\nSPEED COMPARISON:")
        log(f"   Python parsing: {python_rate:.0f} variants/sec")
        log(f"   CSV import: {csv_rate:.0f} variants/sec")
        
        if csv_rate > python_rate:
            improvement = csv_rate / python_rate
            full_hours = 3_433_300_000 / csv_rate / 3600
            log(f"   BREAKTHROUGH: {improvement:.1f}x faster!")
            log(f"   Full dataset time: {full_hours:.1f} hours (vs 10.8 hours)")
            
            if full_hours < 3:
                log("   EXCELLENT: <3 hours for full dataset")
            elif full_hours < 6:
                log("   VERY GOOD: <6 hours for full dataset")
            else:
                log(f"   IMPROVEMENT: {full_hours:.1f} hours")
        else:
            log("   CSV not faster - Python method still better")
        
        # Test data quality
        log("\nTesting data quality...")
        sample = client.query("SELECT * FROM csv_test.splice_csv WHERE gene_symbol != '' LIMIT 3").result_rows
        
        if sample:
            log(f"Sample data with genes:")
            for row in sample:
                log(f"   {row[5]}: {row[2]} (scores: {row[6]}, {row[7]}, {row[8]}, {row[9]})")
        else:
            log("No gene data found - may need to check parsing")
        
        return csv_rate > python_rate, csv_rate
        
    except Exception as e:
        log(f"ERROR: CSV import test failed - {e}")
        return False, 0

def main():
    log("="*80)
    log("VCF TO CSV CONVERSION FOR CLICKHOUSE OPTIMIZATION")
    log("="*80)
    log("Goal: Test ClickHouse's recommended CSV import approach")
    log("Time estimate: 30-60 minutes for full test")
    
    success, rate = test_csv_import_speed()
    
    log(f"\n{'='*80}")
    log("CSV CONVERSION TEST COMPLETE")
    log('='*80)
    
    if success:
        full_hours = 3_433_300_000 / rate / 3600
        log(f"SUCCESS: CSV import is faster!")
        log(f"Ready to convert full dataset and import in {full_hours:.1f} hours")
        log("NEXT: Convert full VCF to CSV and run optimized import")
    else:
        log(f"CSV import not faster - Python parsing remains best")
        log(f"FALLBACK: Use Python method for full dataset")

if __name__ == "__main__":
    main()
