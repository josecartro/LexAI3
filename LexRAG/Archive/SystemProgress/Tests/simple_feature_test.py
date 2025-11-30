import requests
import time

print("TESTING INDIVIDUAL ENHANCED FEATURES")
print("="*50)

features = [
    ("Basic Health", "http://localhost:8001/health"),
    ("Basic Gene", "http://localhost:8001/analyze/gene/TP53"),
    ("Protein Endpoint", "http://localhost:8001/analyze/gene/BRCA2/proteins"),
    ("Expression Endpoint", "http://localhost:8001/analyze/variant/rs7412/expression"),
    ("Metabolics Drug", "http://localhost:8005/analyze/drug_metabolism/codeine")
]

for name, url in features:
    print(f"\nTesting {name}:")
    try:
        start_time = time.time()
        r = requests.get(url, timeout=15)
        response_time = time.time() - start_time
        
        if r.status_code == 200:
            print(f"  SUCCESS: {response_time:.2f}s")
        else:
            print(f"  FAILED: HTTP {r.status_code} in {response_time:.2f}s")
            
    except Exception as e:
        response_time = time.time() - start_time
        print(f"  ERROR: {str(e)[:30]} in {response_time:.2f}s")

print(f"\nDone testing individual features")
