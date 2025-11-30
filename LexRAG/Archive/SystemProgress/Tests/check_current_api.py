import requests

print("Checking what API is currently running on port 8001...")

try:
    r = requests.get("http://localhost:8001/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print("[RUNNING] API is responding")
        print(f"Service: {data.get('service', 'unknown')}")
        print(f"Architecture: {data.get('architecture', 'unknown')}")
        
        # Check which endpoints are available
        r2 = requests.get("http://localhost:8001/openapi.json", timeout=5)
        if r2.status_code == 200:
            schema = r2.json()
            endpoints = list(schema.get('paths', {}).keys())
            print(f"Available endpoints: {endpoints}")
            
            # Check if GraphQL is working
            if "/graphql" in endpoints:
                print("GraphQL endpoint detected")
        
    else:
        print(f"[ERROR] HTTP {r.status_code}")
        
except Exception as e:
    print(f"[OFFLINE] API not responding: {e}")

# Also check what files we have
from pathlib import Path
print(f"\nFiles in LexAPI_Genomics:")
for file in Path(".").glob("*.py"):
    print(f"  - {file.name}")

print(f"\nCurrently running API is using one of these files")
