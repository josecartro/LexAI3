import requests
import time

print("Testing LexAPI_Genomics health check...")
time.sleep(5)

try:
    r = requests.get("http://localhost:8001/health", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("[SUCCESS] LexAPI_Genomics is running!")
        print(f"Service: {data.get('service', 'unknown')}")
        print(f"Architecture: {data.get('architecture', 'unknown')}")
        
        databases = data.get('databases', {})
        print("Database connections:")
        for db_name, db_info in databases.items():
            status = db_info.get('status', 'unknown')
            print(f"  {db_name}: {status}")
            
        # Test variant endpoint
        print("\nTesting variant analysis endpoint...")
        r2 = requests.get("http://localhost:8001/analyze/variant/rs7412", timeout=15)
        if r2.status_code == 200:
            data2 = r2.json()
            print("[SUCCESS] Variant analysis working")
            print(f"Summary: {data2.get('summary', 'No summary')}")
        else:
            print(f"[ERROR] Variant analysis: HTTP {r2.status_code}")
            
    else:
        print(f"[ERROR] HTTP {r.status_code}")
        
except Exception as e:
    print(f"[ERROR] {e}")

print("\nAPI test complete")
