"""
Debug Genomics API Issues
Test each endpoint individually to identify problems
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, description="", timeout=30):
    """Test individual endpoint with detailed error reporting"""
    print(f"\\nTesting: {url}")
    if description:
        print(f"Purpose: {description}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        duration = time.time() - start_time
        
        print(f"Response time: {duration:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"SUCCESS: {len(str(data))} characters returned")
                return {"success": True, "data": data, "duration": duration}
            except json.JSONDecodeError:
                print(f"ERROR: Invalid JSON response")
                print(f"Response text: {response.text[:200]}...")
                return {"success": False, "error": "Invalid JSON"}
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        print(f"ERROR: Request timed out after {timeout} seconds")
        return {"success": False, "error": "Timeout"}
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error - {e}")
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        return {"success": False, "error": str(e)}

def debug_genomics_api():
    """Debug Genomics API systematically"""
    
    print("DEBUGGING GENOMICS API")
    print("="*50)
    print("Testing each endpoint individually")
    print("="*50)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Basic health endpoint
    print("\\n" + "="*40)
    print("TEST 1: Basic Health Check")
    print("="*40)
    
    health_result = test_endpoint(f"{base_url}/health", "Basic API health check", timeout=15)
    
    if health_result["success"]:
        health_data = health_result["data"]
        print("HEALTH CHECK SUCCESS:")
        print(f"  Status: {health_data.get('status')}")
        print(f"  Service: {health_data.get('service')}")
        
        databases = health_data.get("databases", {})
        print(f"  Databases: {list(databases.keys())}")
        
        for db_name, db_info in databases.items():
            print(f"    {db_name}: {db_info.get('status', 'unknown')}")
            if 'total_records' in db_info:
                print(f"      Records: {db_info['total_records']}")
    else:
        print(f"HEALTH CHECK FAILED: {health_result['error']}")
        print("Cannot proceed with other tests if health check fails")
        return False
    
    # Test 2: Simple gene query
    print("\\n" + "="*40)
    print("TEST 2: Simple Gene Query")
    print("="*40)
    
    gene_result = test_endpoint(f"{base_url}/analyze/gene/BRCA1", "Simple BRCA1 gene analysis", timeout=30)
    
    if gene_result["success"]:
        gene_data = gene_result["data"]
        print("GENE QUERY SUCCESS:")
        print(f"  Gene: {gene_data.get('gene_symbol')}")
        
        variants = gene_data.get("variants", {})
        print(f"  Total variants: {variants.get('total_variants', 0):,}")
        print(f"  Pathogenic variants: {variants.get('pathogenic_variants', 0):,}")
        
        expression = gene_data.get("gtex_expression_summary", {})
        print(f"  Expression effects: {expression.get('variants_with_expression_effects', 0):,}")
    else:
        print(f"GENE QUERY FAILED: {gene_result['error']}")
    
    # Test 3: Protein connections endpoint
    print("\\n" + "="*40)
    print("TEST 3: Protein Connections")
    print("="*40)
    
    protein_result = test_endpoint(f"{base_url}/analyze/gene/BRCA1/proteins", "BRCA1 protein connections", timeout=20)
    
    if protein_result["success"]:
        protein_data = protein_result["data"]
        print("PROTEIN QUERY SUCCESS:")
        
        protein_analysis = protein_data.get("protein_analysis", {})
        print(f"  Proteins found: {protein_analysis.get('total_proteins', 0)}")
        print(f"  Connection source: {protein_analysis.get('connection_source', 'unknown')}")
    else:
        print(f"PROTEIN QUERY FAILED: {protein_result['error']}")
    
    # Test 4: Variant query endpoint
    print("\\n" + "="*40)
    print("TEST 4: Variant Analysis")
    print("="*40)
    
    variant_result = test_endpoint(f"{base_url}/query/variants?gene=TP53&pathogenic_only=true", "TP53 pathogenic variants", timeout=25)
    
    if variant_result["success"]:
        variant_data = variant_result["data"]
        print("VARIANT QUERY SUCCESS:")
        print(f"  Variants found: {variant_data.get('total_results', 0)}")
        
        variants = variant_data.get("variants", [])
        if variants:
            print(f"  Sample variant: {variants[0].get('rsid', 'unknown')}")
    else:
        print(f"VARIANT QUERY FAILED: {variant_result['error']}")
    
    # Test 5: Expression analysis
    print("\\n" + "="*40)
    print("TEST 5: Expression Analysis")
    print("="*40)
    
    # This endpoint might not exist, but let's test
    expression_result = test_endpoint(f"{base_url}/analyze/variant/rs7412/expression", "APOE variant expression", timeout=20)
    
    if expression_result["success"]:
        print("EXPRESSION QUERY SUCCESS:")
        expr_data = expression_result["data"]
        print(f"  Expression analysis available")
    else:
        print(f"EXPRESSION QUERY RESULT: {expression_result['error']}")
        print("  Note: This endpoint might not be implemented")
    
    # Summary
    print("\\n" + "="*50)
    print("GENOMICS API DEBUG SUMMARY")
    print("="*50)
    
    tests = [health_result, gene_result, protein_result, variant_result]
    successful_tests = sum(1 for test in tests if test["success"])
    
    print(f"Successful tests: {successful_tests}/{len(tests)}")
    print(f"Health check: {'PASS' if health_result['success'] else 'FAIL'}")
    print(f"Gene analysis: {'PASS' if gene_result['success'] else 'FAIL'}")
    print(f"Protein connections: {'PASS' if protein_result['success'] else 'FAIL'}")
    print(f"Variant queries: {'PASS' if variant_result['success'] else 'FAIL'}")
    
    if successful_tests >= 3:
        print("\\nCONCLUSION: Genomics API is mostly functional")
        print("Issues may be with specific endpoints or timeout settings")
    else:
        print("\\nCONCLUSION: Genomics API has significant issues")
        print("May need to restart the API or check ClickHouse connection")
    
    return successful_tests >= 3

if __name__ == "__main__":
    print("GENOMICS API DEBUGGING")
    print("Testing individual endpoints to isolate issues")
    print("="*50)
    
    success = debug_genomics_api()
    
    if success:
        print("\\nGENOMICS API: Mostly working - proceed with AI integration")
    else:
        print("\\nGENOMICS API: Needs attention before AI integration")
    
    input("Press Enter to continue...")
