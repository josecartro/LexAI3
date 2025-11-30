"""
Test ClickHouse HTTP with Fresh Container
Create new test container using official documentation examples
"""

import subprocess
import time
import requests

def create_test_clickhouse():
    """Create test ClickHouse container using official documentation"""
    
    print("Creating test ClickHouse container using official documentation...")
    print("Based on: https://clickhouse.com/docs/install/docker")
    print("="*60)
    
    # Use exact command from documentation with authentication
    cmd = [
        "docker", "run", "-d",
        "--name", "clickhouse-test-http",
        "-p", "8126:8123",  # Use port 8126 to avoid conflicts
        "-p", "9003:9000",
        "-e", "CLICKHOUSE_USER=testuser",
        "-e", "CLICKHOUSE_PASSWORD=testpass",
        "-e", "CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1",
        "--ulimit", "nofile=262144:262144",
        "clickhouse/clickhouse-server"
    ]
    
    print("Command:", " ".join(cmd))
    print("\\nStarting test container...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"✅ Test container created: {container_id[:12]}")
            return container_id
        else:
            print(f"❌ Container creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating container: {e}")
        return None

def test_http_interface(port=8126):
    """Test ClickHouse HTTP interface"""
    
    print(f"\\nTesting HTTP interface on port {port}...")
    print("Waiting 30 seconds for ClickHouse to start...")
    time.sleep(30)
    
    # Test 1: Basic ping
    print("\\n1. Testing basic ping...")
    try:
        response = requests.get(f"http://localhost:{port}/ping", timeout=10)
        if response.status_code == 200:
            print(f"✅ Ping successful: {response.text}")
        else:
            print(f"❌ Ping failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Ping error: {e}")
    
    # Test 2: Simple query without auth
    print("\\n2. Testing simple query (no auth)...")
    try:
        response = requests.get(f"http://localhost:{port}/?query=SELECT%201", timeout=10)
        if response.status_code == 200:
            print(f"✅ Simple query works: {response.text}")
        else:
            print(f"❌ Query failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Test 3: Query with authentication
    print("\\n3. Testing with authentication...")
    try:
        auth_url = f"http://localhost:{port}/?user=testuser&password=testpass&query=SELECT%20version()"
        response = requests.get(auth_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Authenticated query works: {response.text}")
        else:
            print(f"❌ Auth query failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Auth query error: {e}")
    
    # Test 4: Python clickhouse-connect
    print("\\n4. Testing Python clickhouse-connect...")
    try:
        import clickhouse_connect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=port,
            username='testuser',
            password='testpass'
        )
        
        result = client.query('SELECT version()').result_rows[0][0]
        print(f"✅ Python client works: ClickHouse {result}")
        
        # Test table creation
        client.command("CREATE DATABASE IF NOT EXISTS test_db")
        client.command("""
            CREATE TABLE IF NOT EXISTS test_db.test_table (
                id Int32,
                message String
            ) ENGINE = MergeTree()
            ORDER BY id
        """)
        
        # Test data insertion
        client.insert('test_db.test_table', [(1, 'Hello ClickHouse!')])
        
        # Test data query
        test_result = client.query("SELECT message FROM test_db.test_table WHERE id = 1").result_rows[0][0]
        print(f"✅ Full functionality works: {test_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Python client error: {e}")
        return False

def cleanup_test_container():
    """Clean up test container"""
    print("\\nCleaning up test container...")
    
    try:
        subprocess.run(["docker", "stop", "clickhouse-test-http"], capture_output=True)
        subprocess.run(["docker", "rm", "clickhouse-test-http"], capture_output=True)
        print("✅ Test container cleaned up")
    except:
        print("⚠️ Cleanup may have issues (container might not exist)")

def main():
    """Run complete ClickHouse HTTP test"""
    
    print("CLICKHOUSE HTTP INTERFACE TEST")
    print("="*60)
    print("Testing with fresh container using official documentation")
    print("NO EXISTING DATA WILL BE TOUCHED")
    print("="*60)
    
    # Create test container
    container_id = create_test_clickhouse()
    
    if not container_id:
        print("❌ Cannot proceed - container creation failed")
        return False
    
    # Test HTTP interface
    http_works = test_http_interface()
    
    if http_works:
        print("\\n🎉 SUCCESS: ClickHouse HTTP interface is working!")
        print("The issue is with our existing containers, not ClickHouse itself")
        print("We can compare configurations to fix the original containers")
    else:
        print("\\n❌ FAILURE: Even fresh ClickHouse HTTP doesn't work")
        print("This suggests a system-level issue (firewall, network, etc.)")
    
    # Cleanup
    cleanup_test_container()
    
    return http_works

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n✅ ClickHouse HTTP CAN work - we can fix the original containers")
    else:
        print("\\n❌ ClickHouse HTTP fundamentally broken - system-level issue")
    
    input("Press Enter to continue...")
