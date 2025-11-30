import requests
import subprocess
import time

print("TESTING PERSISTENCE WITH OFFICIAL SETUP")
print("="*50)

# Create test data
print("1. Creating test data...")
r = requests.post("http://localhost:8123/?password=simple123", data="CREATE DATABASE IF NOT EXISTS persist_test")
print(f"Database: {r.status_code}")

r = requests.post("http://localhost:8123/?password=simple123", data="""
    CREATE TABLE persist_test.genes (
        id UInt32,
        name String
    ) ENGINE = MergeTree()
    ORDER BY id
""")
print(f"Table: {r.status_code}")

r = requests.post("http://localhost:8123/?password=simple123", data="INSERT INTO persist_test.genes VALUES (1, 'BRCA1'), (2, 'BRCA2')")
print(f"Insert: {r.status_code}")

r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(*) FROM persist_test.genes")
count_before = r.text.strip()
print(f"Count before restart: {count_before}")

# Restart container
print("2. Restarting container...")
subprocess.run("docker restart clickhouse-persistent", shell=True, capture_output=True)
time.sleep(15)

# Check after restart
print("3. Checking after restart...")
r = requests.post("http://localhost:8123/?password=simple123", data="SHOW DATABASES")
databases = r.text.strip()
print(f"Databases: {databases}")

if "persist_test" in databases:
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(*) FROM persist_test.genes")
    count_after = r.text.strip()
    print(f"Count after restart: {count_after}")
    
    if count_after == count_before:
        print("SUCCESS: Official persistence working!")
        print("Ready for production data migration")
    else:
        print("FAILED: Data lost")
else:
    print("FAILED: Database lost")

print("\nPersistence test complete")

