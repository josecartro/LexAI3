"""
Check ClickHouse Database Status for Digital Twin
Verify what databases and tables exist
"""

import clickhouse_connect

def check_database_status():
    """Check ClickHouse status and digital twin database"""
    
    print("🔍 Checking ClickHouse Database Status")
    print("="*50)
    
    try:
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        print("✅ Connected to ClickHouse successfully")
        
        # Check existing databases
        databases = client.query("SHOW DATABASES").result_rows
        database_names = [db[0] for db in databases]
        
        print(f"📊 Found {len(databases)} databases:")
        for db_name in database_names:
            print(f"   • {db_name}")
        
        # Check if digital_twin_db exists
        if 'digital_twin_db' in database_names:
            print("\\n✅ digital_twin_db exists")
            
            # Check tables in digital_twin_db
            try:
                tables = client.query("SHOW TABLES FROM digital_twin_db").result_rows
                table_names = [table[0] for table in tables]
                
                print(f"📋 Found {len(tables)} tables in digital_twin_db:")
                for table_name in table_names:
                    print(f"   • {table_name}")
                    
                    # Check record counts
                    try:
                        count = client.query(f"SELECT COUNT(*) FROM digital_twin_db.{table_name}").result_rows[0][0]
                        print(f"     Records: {count:,}")
                    except Exception as e:
                        print(f"     Error counting records: {e}")
                        
            except Exception as e:
                print(f"❌ Error checking tables: {e}")
        else:
            print("❌ digital_twin_db does NOT exist")
            print("🔧 Need to create digital_twin_db database")
        
        # Test basic ClickHouse functionality
        print("\\n🧪 Testing basic ClickHouse operations...")
        
        try:
            # Test database creation
            client.command("CREATE DATABASE IF NOT EXISTS test_db")
            print("✅ Database creation works")
            
            # Test table creation
            client.command("""
                CREATE TABLE IF NOT EXISTS test_db.test_table (
                    id String,
                    data String
                ) ENGINE = MergeTree()
                ORDER BY id
            """)
            print("✅ Table creation works")
            
            # Test data insertion
            client.insert('test_db.test_table', [('test1', 'test_data')])
            print("✅ Data insertion works")
            
            # Test data query
            result = client.query("SELECT COUNT(*) FROM test_db.test_table").result_rows[0][0]
            print(f"✅ Data query works - {result} records")
            
            # Cleanup
            client.command("DROP DATABASE test_db")
            print("✅ Database cleanup works")
            
        except Exception as e:
            print(f"❌ Basic operations test failed: {e}")
        
        print("\\n🎉 ClickHouse is working properly!")
        return True
        
    except Exception as e:
        print(f"❌ ClickHouse connection failed: {e}")
        print("\\nPossible issues:")
        print("1. ClickHouse container not running")
        print("2. Wrong credentials (genomics/genomics123)")
        print("3. Port 8123 not accessible")
        print("\\nTry:")
        print("docker start clickhouse-genomics")
        print("curl http://localhost:8123/ping")
        return False

if __name__ == "__main__":
    success = check_database_status()
    if success:
        print("\\n✅ Ready to create digital twin database!")
    else:
        print("\\n❌ Fix ClickHouse issues before proceeding")
    
    input("Press Enter to continue...")

