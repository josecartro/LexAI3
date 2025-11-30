import requests

print("Testing LexAPI_Literature health...")
try:
    r = requests.get("http://localhost:8003/health", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("[SUCCESS] LexAPI_Literature is running!")
        print(f"Service: {data.get('service', 'unknown')}")
        
        databases = data.get('databases', {})
        print("Database connections:")
        for db_name, db_info in databases.items():
            status = db_info.get('status', 'unknown')
            print(f"  {db_name}: {status}")
    else:
        print(f"[ERROR] HTTP {r.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")
