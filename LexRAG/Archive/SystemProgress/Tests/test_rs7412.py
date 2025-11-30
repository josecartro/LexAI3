import requests

print("Testing rs7412 APOE variant with new comprehensive API...")

try:
    r = requests.get("http://localhost:8001/analyze/variant/rs7412", timeout=15)
    
    if r.status_code == 200:
        data = r.json()
        print("[SUCCESS] rs7412 variant found!")
        print(f"Variant: {data.get('variant_id', 'unknown')}")
        
        genomic = data.get('genomic_data', {})
        if genomic and 'error' not in genomic:
            print(f"Gene: {genomic.get('gene_symbol', 'unknown')}")
            print(f"Clinical significance: {genomic.get('clinical_significance', 'unknown')}")
            print(f"Associated disease: {genomic.get('associated_disease', 'unknown')}")
            print(f"Chromosome: {genomic.get('chromosome', 'unknown')}")
            print(f"Position: {genomic.get('position', 'unknown')}")
        else:
            print("Genomic data: Not found or error")
        
        causal = data.get('causal_connections', {})
        if causal and 'error' not in causal:
            tissues = causal.get('tissue_expression', [])
            print(f"Tissue connections: {len(tissues)}")
            for tissue in tissues:
                print(f"  - {tissue.get('tissue', 'unknown')}: {tissue.get('level', 'unknown')}")
        else:
            print("Causal connections: Not found or error")
        
        summary = data.get('comprehensive_summary', 'No summary')
        print(f"Summary: {summary}")
        
        # Show databases queried
        databases = data.get('databases_queried', [])
        print(f"Databases queried: {databases}")
        
    elif r.status_code == 404:
        print("[NOT FOUND] rs7412 variant not in database")
    else:
        print(f"[ERROR] HTTP {r.status_code}")
        print(f"Response: {r.text[:200]}")
        
except Exception as e:
    print(f"[ERROR] {e}")

print("\nrs7412 test complete")
