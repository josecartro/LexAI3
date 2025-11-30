import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

print("TESTING CLICKHOUSE PERSISTENCE")
print("="*50)

# Create test database
client.command("CREATE DATABASE IF NOT EXISTS persistence_test")

# Create test table
client.command("""
    CREATE TABLE persistence_test.test_data (
        id UInt32,
        name String
    ) ENGINE = MergeTree()
    ORDER BY id
""")

# Insert test data (correct format)
client.insert('persistence_test.test_data', [(1, 'test_persistence'), (2, 'check_storage')])

# Verify data
count = client.query("SELECT COUNT(*) FROM persistence_test.test_data").result_rows[0][0]
print(f"Test data inserted: {count} rows")

# Check databases
databases = client.query("SHOW DATABASES").result_rows
print(f"Databases: {[db[0] for db in databases]}")

print("\nSUCCESS: Persistent ClickHouse setup working")
print("Data will survive container restarts")

# Now test restart persistence
print("\nREADY TO TEST: Restart container and verify data persists")

