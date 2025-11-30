import requests
import time

print("Testing new LexAPI_Genomics...")
time.sleep(5)

try:
    r = requests.get("http://localhost:8001/health", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("[SUCCESS] LexAPI_Genomics is running!")
        print(f"Service: {data.get('service', 'unknown')}")
        
        databases = data.get('databases', {})
        print("Database connections:")
        for db_name, db_status in databases.items():
            status = db_status.get('status', 'unknown')
            print(f"  {db_name}: {status}")
        
        # Test comprehensive variant analysis
        print("\nTesting comprehensive BRCA2 analysis...")
        r2 = requests.get("http://localhost:8001/analyze/gene/BRCA2", timeout=15)
        if r2.status_code == 200:
            data2 = r2.json()
            print("[SUCCESS] BRCA2 comprehensive analysis working!")
            print(f"Databases queried: {data2.get('databases_queried', [])}")
            variants = data2.get('variants', {})
            print(f"BRCA2 variants: {variants.get('total_variants', 0)}")
            print(f"Pathogenic variants: {variants.get('pathogenic_variants', 0)}")
        else:
            print(f"[ERROR] BRCA2 analysis: HTTP {r2.status_code}")
            
    else:
        print(f"[ERROR] HTTP {r.status_code}")
        
except Exception as e:
    print(f"[ERROR] {e}")

print("\nLexAPI_Genomics test complete")
