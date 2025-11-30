import requests

print("TESTING CLICKHOUSE WITH FIXED PERMISSIONS")
print("="*50)

# Test basic connection
r = requests.post("http://localhost:8123/?password=simple123", data="SELECT 1")
print(f"Basic query: {r.status_code} - {r.text.strip()}")

# Test data insertion
print("Testing data insertion...")
r = requests.post("http://localhost:8123/?password=simple123", data="CREATE DATABASE IF NOT EXISTS test_fixed")
print(f"Database: {r.status_code}")

r = requests.post("http://localhost:8123/?password=simple123", data="""
    CREATE TABLE test_fixed.permission_test (
        id UInt32,
        name String
    ) ENGINE = MergeTree()
    ORDER BY id
""")
print(f"Table: {r.status_code}")

r = requests.post("http://localhost:8123/?password=simple123", data="INSERT INTO test_fixed.permission_test VALUES (1, 'test'), (2, 'fixed')")
print(f"Insert: {r.status_code}")

if r.status_code == 200:
    print("SUCCESS: Permissions fixed!")
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(*) FROM test_fixed.permission_test")
    print(f"Count: {r.text.strip()} rows")
    print("Ready for production data migration")
else:
    print(f"FAILED: Still permission issues - {r.text}")

print("Permission test complete")

