import requests

print("SIMPLE TRUTH CHECK - What Actually Works")
print("="*50)

# Test LexAPI_Genomics
print("\n1. LexAPI_Genomics:")
try:
    r = requests.get("http://localhost:8001/analyze/gene/BRCA2", timeout=15)
    if r.status_code == 200:
        data = r.json()
        databases = data.get('databases_queried', [])
        print(f"   Databases: {len(databases)} - {databases}")
        
        # Check what's actually in the response
        keys = list(data.keys())
        print(f"   Response keys: {keys}")
        
        # Check specific enhancements
        if 'gtex_expression_summary' in data:
            gtex = data['gtex_expression_summary']
            if 'error' not in gtex:
                print(f"   ✅ GTEx expression: WORKING")
            else:
                print(f"   ❌ GTEx expression: {gtex.get('error', 'unknown error')}")
        else:
            print(f"   ❌ GTEx expression: Key not found")
            
    else:
        print(f"   ❌ Not responding: HTTP {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test individual endpoints that should work
print("\n2. Individual Endpoints:")
try:
    r = requests.get("http://localhost:8001/analyze/variant/rs7412/expression", timeout=10)
    if r.status_code == 200:
        data = r.json()
        expression = data.get('expression_analysis', {})
        if 'total_tissues_affected' in expression:
            print(f"   ✅ Expression endpoint: {expression['total_tissues_affected']} tissues")
        else:
            print(f"   ❌ Expression endpoint: No data")
    else:
        print(f"   ❌ Expression endpoint: HTTP {r.status_code}")
except Exception as e:
    print(f"   ❌ Expression endpoint: {e}")

try:
    r = requests.get("http://localhost:8001/analyze/variant/rs7412/splicing", timeout=10)
    if r.status_code == 200:
        data = r.json()
        splicing = data.get('splicing_analysis', {})
        if 'total_splice_events' in splicing:
            print(f"   ✅ Splicing endpoint: {splicing['total_splice_events']} events")
        else:
            print(f"   ❌ Splicing endpoint: No data")
    else:
        print(f"   ❌ Splicing endpoint: HTTP {r.status_code}")
except Exception as e:
    print(f"   ❌ Splicing endpoint: {e}")

print("\n" + "="*50)
print("TRUTH: What actually works vs what we claim")
print("="*50)
