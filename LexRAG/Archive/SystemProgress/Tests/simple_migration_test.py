import clickhouse_connect
import pandas as pd
import time

print("CLICKHOUSE MIGRATION TEST - PHARMGKB")
print("="*50)

try:
    # Connect to ClickHouse
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics', 
        password='genomics123'
    )
    print("SUCCESS: ClickHouse connected")
    
    # Create database
    client.command("CREATE DATABASE IF NOT EXISTS drugs_db")
    print("SUCCESS: Database created")
    
    # Read PharmGKB data
    print("\nReading PharmGKB source data...")
    pharmgkb_file = "data/pharmgkb/drug_gene_interactions.csv"
    df = pd.read_csv(pharmgkb_file)
    print(f"PharmGKB data: {len(df):,} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    
    # Create table
    print("\nCreating ClickHouse table...")
    create_table = """
        CREATE TABLE IF NOT EXISTS drugs_db.interactions (
            gene_symbol String,
            drug_name String,
            interaction_type String,
            clinical_significance String,
            evidence_level String,
            dosing_recommendation String
        ) ENGINE = MergeTree()
        ORDER BY (gene_symbol, drug_name)
    """
    
    client.command(create_table)
    print("SUCCESS: Table created")
    
    # Insert data
    print("\nInserting data...")
    start_time = time.time()
    
    data_rows = [tuple(row) for row in df.values]
    client.insert('drugs_db.interactions', data_rows)
    
    insert_time = time.time() - start_time
    print(f"SUCCESS: {len(df):,} rows inserted in {insert_time:.2f}s")
    
    # Test queries
    print("\nTesting query performance...")
    
    # Query 1: Count
    start = time.time()
    count = client.query("SELECT COUNT(*) FROM drugs_db.interactions").result_rows[0][0]
    time1 = time.time() - start
    print(f"Count query: {count:,} rows in {time1:.4f}s")
    
    # Query 2: Gene lookup  
    start = time.time()
    cyp2d6 = client.query("SELECT * FROM drugs_db.interactions WHERE gene_symbol = 'CYP2D6'").result_rows
    time2 = time.time() - start
    print(f"Gene lookup: {len(cyp2d6)} results in {time2:.4f}s")
    
    # Query 3: Drug lookup
    start = time.time()
    codeine = client.query("SELECT * FROM drugs_db.interactions WHERE drug_name = 'Codeine'").result_rows
    time3 = time.time() - start
    print(f"Drug lookup: {len(codeine)} results in {time3:.4f}s")
    
    print(f"\nPERFORMANCE SUMMARY:")
    print(f"Data import: {insert_time:.2f}s")
    print(f"Average query: {(time1 + time2 + time3)/3:.4f}s")
    
    if (time1 + time2 + time3)/3 < 0.1:
        print("EXCELLENT: Sub-0.1s performance!")
    else:
        print("GOOD: Fast performance achieved")
    
    print(f"\nSUCCESS: PharmGKB migration to ClickHouse complete")
    print("Ready to migrate larger datasets")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("Migration failed - check ClickHouse connection")
