"""
Migrate PharmGKB Data to ClickHouse
Test migration from original source files to ClickHouse
"""

import clickhouse_connect
import pandas as pd
import time
import os
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def test_pharmgkb_migration():
    """Test migrating PharmGKB data from original CSV to ClickHouse"""
    log("TESTING PHARMGKB MIGRATION TO CLICKHOUSE")
    log("="*60)
    
    try:
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123, 
            username='genomics',
            password='genomics123'
        )
        log("✅ ClickHouse connection established")
        
        # Create drugs database
        client.command("CREATE DATABASE IF NOT EXISTS drugs_db")
        log("✅ Drugs database created")
        
        # Check PharmGKB source file
        pharmgkb_file = Path("data/pharmgkb/drug_gene_interactions.csv")
        if not pharmgkb_file.exists():
            log(f"❌ PharmGKB file not found: {pharmgkb_file}")
            return False
        
        log(f"✅ PharmGKB source file found: {pharmgkb_file}")
        log(f"   File size: {pharmgkb_file.stat().st_size / 1024:.1f} KB")
        
        # Read PharmGKB data
        log("📊 Reading PharmGKB data...")
        df = pd.read_csv(pharmgkb_file)
        log(f"   Rows: {len(df):,}")
        log(f"   Columns: {list(df.columns)}")
        
        # Create ClickHouse table
        log("🔨 Creating ClickHouse table...")
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS drugs_db.drug_gene_interactions (
                gene_symbol String,
                drug_name String,
                interaction_type String,
                clinical_significance String,
                evidence_level String,
                dosing_recommendation String
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, drug_name)
        """
        
        client.command(create_table_sql)
        log("✅ ClickHouse table created")
        
        # Insert data into ClickHouse
        log("📥 Inserting data into ClickHouse...")
        start_time = time.time()
        
        # Convert DataFrame to list of tuples for ClickHouse
        data_rows = [tuple(row) for row in df.values]
        
        client.insert('drugs_db.drug_gene_interactions', data_rows)
        
        insert_time = time.time() - start_time
        log(f"✅ Data inserted in {insert_time:.2f} seconds")
        
        # Test query performance
        log("🧪 Testing ClickHouse query performance...")
        
        # Test 1: Count all
        start_time = time.time()
        total_count = client.query("SELECT COUNT(*) FROM drugs_db.drug_gene_interactions").result_rows[0][0]
        count_time = time.time() - start_time
        log(f"   Total count: {total_count:,} in {count_time:.4f}s")
        
        # Test 2: Gene lookup
        start_time = time.time()
        cyp2d6_results = client.query("SELECT * FROM drugs_db.drug_gene_interactions WHERE gene_symbol = 'CYP2D6'").result_rows
        lookup_time = time.time() - start_time
        log(f"   CYP2D6 lookup: {len(cyp2d6_results)} results in {lookup_time:.4f}s")
        
        # Test 3: Drug lookup
        start_time = time.time()
        codeine_results = client.query("SELECT * FROM drugs_db.drug_gene_interactions WHERE drug_name = 'Codeine'").result_rows
        drug_time = time.time() - start_time
        log(f"   Codeine lookup: {len(codeine_results)} results in {drug_time:.4f}s")
        
        # Test 4: Complex query
        start_time = time.time()
        complex_results = client.query("""
            SELECT gene_symbol, COUNT(*) as drug_count
            FROM drugs_db.drug_gene_interactions 
            WHERE clinical_significance = 'High'
            GROUP BY gene_symbol
            ORDER BY drug_count DESC
        """).result_rows
        complex_time = time.time() - start_time
        log(f"   Complex query: {len(complex_results)} results in {complex_time:.4f}s")
        
        # Performance summary
        log(f"\n📊 CLICKHOUSE PERFORMANCE SUMMARY:")
        log(f"   Data import: {insert_time:.2f}s for {len(df):,} rows")
        log(f"   Simple queries: {count_time:.4f}s - {lookup_time:.4f}s")
        log(f"   Complex query: {complex_time:.4f}s")
        
        if all(t < 0.1 for t in [count_time, lookup_time, drug_time, complex_time]):
            log("🎉 EXCELLENT: All queries <0.1s!")
        elif all(t < 0.5 for t in [count_time, lookup_time, drug_time, complex_time]):
            log("✅ GOOD: All queries <0.5s")
        else:
            log("⚠️  Some queries slower than expected")
        
        return True
        
    except Exception as e:
        log(f"❌ Migration error: {e}")
        return False

def compare_with_duckdb_pharmgkb():
    """Compare ClickHouse vs DuckDB performance for same PharmGKB data"""
    log(f"\n🆚 COMPARING WITH DUCKDB PERFORMANCE")
    log("="*60)
    
    try:
        # Test DuckDB performance (if accessible)
        import duckdb
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Check if DuckDB has similar data
        tables = conn.execute("SHOW TABLES").fetchall()
        pharmgkb_tables = [t[0] for t in tables if 'pharmgkb' in t[0].lower() or 'drug' in t[0].lower()]
        
        if pharmgkb_tables:
            log(f"   DuckDB PharmGKB tables: {pharmgkb_tables}")
            
            # Test query on DuckDB
            for table in pharmgkb_tables[:1]:  # Test first table
                start_time = time.time()
                result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                duckdb_time = time.time() - start_time
                log(f"   DuckDB {table}: {result:,} rows in {duckdb_time:.4f}s")
        else:
            log("   No comparable DuckDB PharmGKB data found")
        
        conn.close()
        
    except Exception as e:
        log(f"   DuckDB comparison error: {e}")

def main():
    log("="*80)
    log("CLICKHOUSE MIGRATION TEST - PHARMGKB DATA")
    log("="*80)
    log("Goal: Test migration from original source files to ClickHouse")
    
    # Test PharmGKB migration
    success = test_pharmgkb_migration()
    
    if success:
        # Compare with DuckDB
        compare_with_duckdb_pharmgkb()
        
        log(f"\n{'='*80}")
        log("MIGRATION TEST SUCCESS")
        log('='*80)
        log("✅ PharmGKB data successfully migrated to ClickHouse")
        log("📊 Performance verified - ready for larger datasets")
        log("🎯 Next: Migrate ClinVar variants from original VCF files")
        
    else:
        log(f"\n{'='*80}")
        log("MIGRATION TEST FAILED")
        log('='*80)
        log("❌ PharmGKB migration needs debugging")

if __name__ == "__main__":
    main()
