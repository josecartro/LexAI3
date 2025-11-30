import requests
import time

print("TESTING SIMPLE CLICKHOUSE FUNCTIONALITY")
print("="*50)

# Test basic connection
try:
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT 1")
    if r.status_code == 200:
        print(f"Basic query: {r.text.strip()}")
    else:
        print(f"Connection failed: {r.status_code}")
        exit()
except Exception as e:
    print(f"Connection error: {e}")
    exit()

# Test database creation
print("\nTesting database creation...")
try:
    r = requests.post("http://localhost:8123/?password=simple123", data="CREATE DATABASE IF NOT EXISTS test_simple")
    if r.status_code == 200:
        print("Database created successfully")
    else:
        print(f"Database creation failed: {r.status_code}")
except Exception as e:
    print(f"Database creation error: {e}")

# Test table creation
print("\nTesting table creation...")
try:
    create_table = """
        CREATE TABLE test_simple.variants (
            rsid String,
            gene String,
            significance String
        ) ENGINE = MergeTree()
        ORDER BY rsid
    """
    
    r = requests.post("http://localhost:8123/?password=simple123", data=create_table)
    if r.status_code == 200:
        print("Table created successfully")
    else:
        print(f"Table creation failed: {r.status_code}")
        print(f"Response: {r.text}")
except Exception as e:
    print(f"Table creation error: {e}")

# Test data insertion
print("\nTesting data insertion...")
try:
    insert_data = """
        INSERT INTO test_simple.variants VALUES 
        ('rs7412', 'APOE', 'Pathogenic'),
        ('rs429358', 'APOE', 'Risk_factor'),
        ('rs80357713', 'BRCA1', 'Pathogenic')
    """
    
    r = requests.post("http://localhost:8123/?password=simple123", data=insert_data)
    if r.status_code == 200:
        print("Data inserted successfully")
        
        # Query the data
        r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(*) FROM test_simple.variants")
        if r.status_code == 200:
            count = r.text.strip()
            print(f"Data count: {count} rows")
            
            # Query specific data
            r = requests.post("http://localhost:8123/?password=simple123", data="SELECT * FROM test_simple.variants")
            if r.status_code == 200:
                print("Sample data:")
                for line in r.text.strip().split('\n'):
                    print(f"   {line}")
                    
                print("\nSUCCESS: Simple ClickHouse working perfectly!")
                print("Basic functionality confirmed")
            
    else:
        print(f"Data insertion failed: {r.status_code}")
        print(f"Response: {r.text}")
        
except Exception as e:
    print(f"Data insertion error: {e}")

print("\nSimple ClickHouse test complete")

