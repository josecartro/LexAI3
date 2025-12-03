"""
Simple ClickHouse HTTP Test (Windows Compatible)
Test fresh ClickHouse container using official documentation
"""

import subprocess
import time
import requests

def test_fresh_clickhouse():
    """Test ClickHouse HTTP with fresh container"""
    
    print("CLICKHOUSE HTTP TEST")
    print("="*50)
    print("Creating fresh test container")
    print("Based on official documentation")
    print("NO EXISTING DATA TOUCHED")
    print("="*50)
    
    # Create test container using official documentation approach
    cmd = [
        "docker", "run", "-d",
        "--name", "clickhouse-test-simple",
        "-p", "8127:8123",  # Use port 8127 for test
        "-p", "9004:9000",
        "-e", "CLICKHOUSE_USER=testuser",
        "-e", "CLICKHOUSE_PASSWORD=testpass", 
        "-e", "CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1",
        "--ulimit", "nofile=262144:262144",
        "clickhouse/clickhouse-server"
    ]
    
    print("Creating test container...")
    print("Command: " + " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"SUCCESS: Test container created - {container_id[:12]}")
        else:
            print(f"ERROR: Container creation failed - {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Wait for startup
    print("\\nWaiting 30 seconds for ClickHouse to start...")
    time.sleep(30)
    
    # Test HTTP interface
    print("\\nTesting HTTP interface on port 8127...")
    
    # Test 1: Basic ping
    print("1. Basic ping test...")
    try:
        response = requests.get("http://localhost:8127/ping", timeout=10)
        print(f"   Ping result: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Ping failed: {e}")
    
    # Test 2: Simple query
    print("\\n2. Simple query test...")
    try:
        response = requests.get("http://localhost:8127/?query=SELECT%201", timeout=10)
        print(f"   Query result: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Query failed: {e}")
    
    # Test 3: With authentication
    print("\\n3. Authenticated query test...")
    try:
        auth_url = "http://localhost:8127/?user=testuser&password=testpass&query=SELECT%20version()"
        response = requests.get(auth_url, timeout=10)
        print(f"   Auth query result: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"   ClickHouse version: {response.text}")
    except Exception as e:
        print(f"   Auth query failed: {e}")
    
    # Test 4: Python clickhouse-connect
    print("\\n4. Python clickhouse-connect test...")
    try:
        import clickhouse_connect
        
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8127,
            username='testuser',
            password='testpass'
        )
        
        version = client.query('SELECT version()').result_rows[0][0]
        print(f"   Python client works: {version}")
        
        # Test database operations
        client.command("CREATE DATABASE IF NOT EXISTS test_db")
        print("   Database creation: SUCCESS")
        
        client.command("""
            CREATE TABLE IF NOT EXISTS test_db.test_table (
                id Int32,
                message String
            ) ENGINE = MergeTree()
            ORDER BY id
        """)
        print("   Table creation: SUCCESS")
        
        client.insert('test_db.test_table', [(1, 'HTTP Test Success!')])
        print("   Data insertion: SUCCESS")
        
        result = client.query("SELECT message FROM test_db.test_table WHERE id = 1").result_rows[0][0]
        print(f"   Data query: SUCCESS - {result}")
        
        print("\\n   SUCCESS: Full ClickHouse HTTP functionality working!")
        return True
        
    except Exception as e:
        print(f"   Python client failed: {e}")
        return False

def cleanup_test():
    """Clean up test container"""
    print("\\nCleaning up test container...")
    try:
        subprocess.run(["docker", "stop", "clickhouse-test-simple"], capture_output=True)
        subprocess.run(["docker", "rm", "clickhouse-test-simple"], capture_output=True)
        print("Test container removed")
    except:
        print("Cleanup completed")

def main():
    """Run complete test"""
    
    # Create and test
    success = test_fresh_clickhouse()
    
    print("\\n" + "="*50)
    print("TEST RESULTS")
    print("="*50)
    
    if success:
        print("SUCCESS: ClickHouse HTTP interface CAN work")
        print("CONCLUSION: Issue is with our existing containers")
        print("NEXT: Compare configurations to fix original containers")
    else:
        print("FAILURE: ClickHouse HTTP fundamentally broken")
        print("CONCLUSION: System-level network/firewall issue")
        print("NEXT: Investigate network configuration")
    
    # Cleanup
    cleanup_test()
    
    return success

if __name__ == "__main__":
    result = main()
    input("\\nPress Enter to continue...")
