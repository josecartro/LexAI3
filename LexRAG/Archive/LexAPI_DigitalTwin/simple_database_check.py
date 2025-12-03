"""
Simple Database Status Check (Windows compatible)
Check ClickHouse status without Unicode characters
"""

import clickhouse_connect

def check_simple_status():
    """Check ClickHouse status - READ ONLY, NO MODIFICATIONS"""
    
    print("Checking ClickHouse Database Status")
    print("="*50)
    
    try:
        # Connect to ClickHouse (READ ONLY)
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        print("SUCCESS: Connected to ClickHouse")
        
        # Check existing databases (READ ONLY)
        databases = client.query("SHOW DATABASES").result_rows
        database_names = [db[0] for db in databases]
        
        print(f"Found {len(databases)} databases:")
        for db_name in database_names:
            print(f"   - {db_name}")
        
        # Check specifically for digital_twin_db (READ ONLY)
        if 'digital_twin_db' in database_names:
            print("\\nSUCCESS: digital_twin_db exists")
            
            # Check tables (READ ONLY)
            tables = client.query("SHOW TABLES FROM digital_twin_db").result_rows
            table_names = [table[0] for table in tables]
            
            print(f"Found {len(tables)} tables in digital_twin_db:")
            for table_name in table_names:
                print(f"   - {table_name}")
                
                # Check record counts (READ ONLY)
                try:
                    count = client.query(f"SELECT COUNT(*) FROM digital_twin_db.{table_name}").result_rows[0][0]
                    print(f"     Records: {count:,}")
                except Exception as e:
                    print(f"     Error counting: {e}")
        else:
            print("\\nNOT FOUND: digital_twin_db does NOT exist")
            print("NEEDED: Need to create digital_twin_db database")
            print("SAFE: Will use CREATE DATABASE IF NOT EXISTS")
        
        return True
        
    except Exception as e:
        print(f"ERROR: ClickHouse connection failed: {e}")
        print("\\nPossible issues:")
        print("1. ClickHouse container not running")
        print("2. Wrong credentials")
        print("3. Port 8123 not accessible")
        return False

if __name__ == "__main__":
    print("READ-ONLY DATABASE STATUS CHECK")
    print("NO MODIFICATIONS WILL BE MADE")
    print("="*50)
    
    success = check_simple_status()
    
    if success:
        print("\\nSUCCESS: ClickHouse is accessible")
        print("SAFE: Can proceed with creating missing databases")
    else:
        print("\\nERROR: ClickHouse issues need to be resolved")
    
    input("Press Enter to continue...")

