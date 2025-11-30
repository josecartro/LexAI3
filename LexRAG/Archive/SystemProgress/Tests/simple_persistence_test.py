import clickhouse_connect
import subprocess
import time

print("SIMPLE CLICKHOUSE PERSISTENCE TEST")
print("="*50)

try:
    client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

    # Create simple test
    client.command("CREATE DATABASE IF NOT EXISTS test_db")
    client.command("DROP TABLE IF EXISTS test_db.simple_test")
    client.command("""
        CREATE TABLE test_db.simple_test (
            id UInt32,
            name String
        ) ENGINE = MergeTree()
        ORDER BY id
    """)

    # Insert using SQL
    client.command("INSERT INTO test_db.simple_test VALUES (1, 'BRCA1'), (2, 'BRCA2'), (3, 'TP53')")

    count_before = client.query("SELECT COUNT(*) FROM test_db.simple_test").result_rows[0][0]
    print(f"Data before restart: {count_before} rows")

    # Restart container
    print("Restarting container...")
    subprocess.run("docker restart clickhouse-genomics", shell=True, capture_output=True)
    time.sleep(20)

    # Check after restart
    client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')
    databases = client.query("SHOW DATABASES").result_rows
    print(f"Databases after restart: {[db[0] for db in databases]}")

    if 'test_db' in [db[0] for db in databases]:
        count_after = client.query("SELECT COUNT(*) FROM test_db.simple_test").result_rows[0][0]
        print(f"Data after restart: {count_after} rows")
        
        if count_after == count_before:
            print("SUCCESS: Official persistence working!")
            print("Ready for production data migration")
        else:
            print("FAILED: Data lost")
    else:
        print("FAILED: Database lost")

except Exception as e:
    print(f"ERROR: {e}")

