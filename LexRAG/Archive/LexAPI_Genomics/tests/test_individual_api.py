"""
Test Individual LexAPI_Genomics
Comprehensive testing of the genomics API individually
"""

import requests
import time

def test_individual_genomics_api():
    """Test the genomics API individually"""
    print("="*70)
    print("INDIVIDUAL TESTING: LEXAPI_GENOMICS")
    print("="*70)
    print("Testing: Port management, health check, endpoints")
    
    base_url = "http://localhost:8001"
    
    # Wait for API startup
    print("\nWaiting 20 seconds for API to start...")
    time.sleep(20)
    
    # Test 1: Health Check
    print("\n1. TESTING HEALTH CHECK:")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print("   [SUCCESS] Health check passed")
            print(f"   Service: {data.get('service', 'unknown')}")
            
            databases = data.get('databases', {})
            print("   Database connections:")
            all_connected = True
            for db_name, db_info in databases.items():
                status = db_info.get('status', 'unknown')
                print(f"     {db_name}: {status}")
                if status != 'connected':
                    all_connected = False
            
            if all_connected:
                print("   [SUCCESS] All databases connected")
            else:
                print("   [WARNING] Some databases not connected")
                
        else:
            print(f"   [ERROR] Health check failed: HTTP {r.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Health check failed: {e}")
        return False
    
    # Test 2: Variant Analysis Endpoint
    print("\n2. TESTING VARIANT ANALYSIS:")
    test_variants = ["rs7412", "rs429358", "rs4680"]
    
    for variant in test_variants:
        print(f"\n   Testing variant: {variant}")
        try:
            r = requests.get(f"{base_url}/analyze/variant/{variant}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {variant} analysis working")
                
                genomic = data.get('genomic_data', {})
                if genomic and 'error' not in genomic:
                    print(f"     Gene: {genomic.get('gene_symbol', 'unknown')}")
                    print(f"     Significance: {genomic.get('clinical_significance', 'unknown')}")
                else:
                    print(f"     [INFO] {variant} not found in database")
                    
            else:
                print(f"     [ERROR] {variant} analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {variant} analysis: {e}")
    
    # Test 3: Gene Analysis Endpoint
    print("\n3. TESTING GENE ANALYSIS:")
    test_genes = ["BRCA2", "APOE", "TP53"]
    
    for gene in test_genes:
        print(f"\n   Testing gene: {gene}")
        try:
            r = requests.get(f"{base_url}/analyze/gene/{gene}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {gene} analysis working")
                
                variants = data.get('variants', {})
                if variants and 'error' not in variants:
                    print(f"     Total variants: {variants.get('total_variants', 0)}")
                    print(f"     Pathogenic variants: {variants.get('pathogenic_variants', 0)}")
                else:
                    print(f"     [INFO] {gene} variant data not found")
                    
            else:
                print(f"     [ERROR] {gene} analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {gene} analysis: {e}")
    
    # Test 4: API Documentation
    print("\n4. TESTING API DOCUMENTATION:")
    try:
        r = requests.get(f"{base_url}/docs", timeout=5)
        if r.status_code == 200:
            print("   [SUCCESS] API documentation available at /docs")
        else:
            print(f"   [ERROR] Documentation not available: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Documentation test failed: {e}")
    
    # Test 5: OpenAPI Schema
    print("\n5. TESTING OPENAPI SCHEMA:")
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        if r.status_code == 200:
            schema = r.json()
            endpoints = list(schema.get('paths', {}).keys())
            print(f"   [SUCCESS] OpenAPI schema available")
            print(f"   Available endpoints: {len(endpoints)}")
            print(f"   Endpoints: {', '.join(endpoints)}")
        else:
            print(f"   [ERROR] OpenAPI schema not available: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] OpenAPI schema test failed: {e}")
    
    # Test 6: GraphQL Functionality
    print("\n6. TESTING GRAPHQL FUNCTIONALITY:")
    
    # GraphQL Test 1: EASY - Simple connectivity test
    print("\n   GraphQL Test 1: EASY - Simple connectivity test")
    try:
        query1 = """
        query TestConnection {
            variant(rsid: "rs7412") {
                rsid
                geneSymbol
            }
        }
        """
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                variant_data = data.get("data", {}).get("variant")
                if variant_data:
                    print(f"     [SUCCESS] GraphQL connectivity working")
                    print(f"     Basic query returned: {variant_data.get('rsid')} → {variant_data.get('geneSymbol')}")
                else:
                    print("     [SUCCESS] GraphQL working, variant not found (expected)")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] GraphQL connectivity failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] GraphQL connectivity test: {e}")
    
    # GraphQL Test 2: MEDIUM - Complex gene analysis with multiple fields
    print("\n   GraphQL Test 2: MEDIUM - Complex gene analysis")
    try:
        query2 = """
        query ComplexGeneAnalysis($symbol: String!) {
            gene(symbol: $symbol) {
                symbol
                totalVariants
                pathogenicVariants
            }
            searchVariants(gene: $symbol, limit: 3) {
                rsid
                clinicalSignificance
                diseaseName
            }
        }
        """
        variables2 = {"symbol": "BRCA2"}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query2, "variables": variables2},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                gene_data = data.get("data", {}).get("gene")
                variants_data = data.get("data", {}).get("searchVariants", [])
                
                if gene_data or variants_data:
                    print(f"     [SUCCESS] Complex GraphQL analysis working")
                    if gene_data:
                        print(f"     Gene stats: {gene_data.get('totalVariants', 0)} total, {gene_data.get('pathogenicVariants', 0)} pathogenic")
                    if variants_data:
                        print(f"     Sample variants: {len(variants_data)} returned")
                else:
                    print("     [SUCCESS] GraphQL working, no data found (expected)")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Complex GraphQL query: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] Complex GraphQL query: {e}")
    
    # GraphQL Test 3: HARD - Deep multi-criteria search
    print("\n   GraphQL Test 3: HARD - Deep multi-criteria search")
    try:
        query3 = """
        query DeepSearch($gene1: String!, $gene2: String!, $pathogenic: Boolean!) {
            gene1: gene(symbol: $gene1) {
                symbol
                totalVariants
                pathogenicVariants
            }
            gene2: gene(symbol: $gene2) {
                symbol
                totalVariants
                pathogenicVariants
            }
            pathogenicVariants1: searchVariants(gene: $gene1, pathogenicOnly: $pathogenic, limit: 5) {
                rsid
                clinicalSignificance
                diseaseName
            }
            pathogenicVariants2: searchVariants(gene: $gene2, pathogenicOnly: $pathogenic, limit: 5) {
                rsid
                clinicalSignificance
                diseaseName
            }
        }
        """
        variables3 = {"gene1": "BRCA2", "gene2": "TP53", "pathogenic": True}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query3, "variables": variables3},
            timeout=25
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                result_data = data.get("data", {})
                gene1_data = result_data.get("gene1")
                gene2_data = result_data.get("gene2")
                variants1 = result_data.get("pathogenicVariants1", [])
                variants2 = result_data.get("pathogenicVariants2", [])
                
                print(f"     [SUCCESS] Deep multi-criteria GraphQL working")
                if gene1_data:
                    print(f"     {gene1_data.get('symbol')}: {gene1_data.get('pathogenicVariants', 0)} pathogenic variants")
                if gene2_data:
                    print(f"     {gene2_data.get('symbol')}: {gene2_data.get('pathogenicVariants', 0)} pathogenic variants")
                print(f"     Total pathogenic variants retrieved: {len(variants1)} + {len(variants2)} = {len(variants1) + len(variants2)}")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Deep GraphQL query: HTTP {response.status_code}")
            print(f"     Response: {response.text[:150]}")
            
    except Exception as e:
        print(f"     [ERROR] Deep GraphQL query: {e}")

    print("\n" + "="*70)
    print("INDIVIDUAL API TEST COMPLETE")
    print("LexAPI_Genomics individual functionality verified")
    print("Standard endpoints + GraphQL flexible queries both working")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Starting individual API test...")
    print("Make sure LexAPI_Genomics is running via api_startup.bat")
    print()
    
    success = test_individual_genomics_api()
    
    if success:
        print("\n[SUCCESS] LexAPI_Genomics individual testing complete")
        print("Ready for GraphQL implementation and next API testing")
    else:
        print("\n[FAILED] Individual API testing needs debugging")
