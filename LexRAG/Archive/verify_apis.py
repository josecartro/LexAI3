"""
LexRAG Comprehensive API Verification Script
Tests all updated APIs (Genomics, Anatomics, Gateway) for ClickHouse/Neo4j connectivity.
"""

import requests
import json
import time

BASE_URLS = {
    "genomics": "http://127.0.0.1:8001",
    "anatomics": "http://127.0.0.1:8002",
    "literature": "http://127.0.0.1:8003",
    "gateway": "http://127.0.0.1:8009"
}

def test_endpoint(name, url):
    print(f"Testing {name} ({url})...", end=" ")
    try:
        start = time.time()
        res = requests.get(url, timeout=10)
        dur = time.time() - start
        if res.status_code == 200:
            data = res.json()
            # Simple check for data presence
            has_data = False
            if isinstance(data, dict):
                # Check typical data keys
                if "genomic_data" in data or "anatomical_structure" in data or "status" == "healthy":
                    has_data = True
                if "error" in data:
                    print(f"⚠️  OK (HTTP 200) but returned error: {data['error']}")
                    return
            
            if has_data:
                print(f"[OK] OK ({dur:.2f}s)")
            else:
                print(f"[?] OK ({dur:.2f}s) - Data payload: {str(data)[:50]}...")
        else:
            print(f"[FAIL] Fail: HTTP {res.status_code}")
            print(res.text[:100])
    except Exception as e:
        print(f"[ERR] Error: {e}")

def main():
    print("=== Verifying API Upgrades (No DuckDB) ===\n")
    
    # 1. Genomics
    print("--- Genomics API ---")
    test_endpoint("Health", f"{BASE_URLS['genomics']}/health")
    test_endpoint("Variant Analysis (BRCA1)", f"{BASE_URLS['genomics']}/analyze/variant/rs12345") # Example
    test_endpoint("Gene Analysis (BRCA1)", f"{BASE_URLS['genomics']}/analyze/gene/BRCA1")
    
    # 2. Anatomics
    print("\n--- Anatomics API ---")
    test_endpoint("Health", f"{BASE_URLS['anatomics']}/health")
    test_endpoint("Organ Analysis (Heart)", f"{BASE_URLS['anatomics']}/analyze/organ/heart")
    
    # 3. Literature
    print("\n--- Literature API ---")
    test_endpoint("Health", f"{BASE_URLS['literature']}/health")
    test_endpoint("Search (Cancer)", f"{BASE_URLS['literature']}/search/literature/cancer")

    # 4. Gateway
    print("\n--- AI Gateway ---")
    test_endpoint("Health", f"{BASE_URLS['gateway']}/health")
    
    print("\nDone.")

if __name__ == "__main__":
    main()

