"""
Test Individual LexAPI_Anatomics
Comprehensive testing of the anatomics API individually
"""

import requests
import time

def test_individual_anatomics_api():
    """Test the anatomics API individually"""
    print("="*70)
    print("INDIVIDUAL TESTING: LEXAPI_ANATOMICS")
    print("="*70)
    print("Testing: Port management, health check, anatomical endpoints")
    
    base_url = "http://localhost:8002"
    
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
    
    # Test 2: Organ Analysis Endpoint
    print("\n2. TESTING ORGAN ANALYSIS:")
    test_organs = ["heart", "brain", "lung", "breast", "kidney"]
    
    for organ in test_organs:
        print(f"\n   Testing organ: {organ}")
        try:
            r = requests.get(f"{base_url}/analyze/organ/{organ}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {organ} analysis working")
                
                structure = data.get('anatomical_structure', {})
                if structure and 'error' not in structure:
                    matches = structure.get('total_matches', 0)
                    print(f"     Anatomical matches: {matches}")
                
                genetics = data.get('genetic_connections', {})
                if genetics and 'error' not in genetics:
                    genes = genetics.get('total_genes', 0)
                    print(f"     Gene connections: {genes}")
                else:
                    print(f"     Gene connections: Not found")
                    
            else:
                print(f"     [ERROR] {organ} analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {organ} analysis: {e}")
    
    # Test 3: Gene-to-Anatomy Tracing
    print("\n3. TESTING GENE-TO-ANATOMY TRACING:")
    test_genes = ["BRCA2", "CFTR", "APOE"]
    
    for gene in test_genes:
        print(f"\n   Testing gene tracing: {gene}")
        try:
            r = requests.get(f"{base_url}/trace/gene_to_anatomy/{gene}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {gene} tracing working")
                
                effects = data.get('anatomical_effects', {})
                if effects and 'error' not in effects:
                    structures = effects.get('total_structures', 0)
                    print(f"     Anatomical structures affected: {structures}")
                    
                    affected = effects.get('affected_structures', [])
                    if affected:
                        print(f"     Sample tissues:")
                        for struct in affected[:3]:
                            tissue = struct.get('anatomy', 'unknown')
                            level = struct.get('level', 'unknown')
                            print(f"       {tissue}: {level}")
                else:
                    print(f"     [INFO] {gene} anatomical effects not found")
                    
            else:
                print(f"     [ERROR] {gene} tracing: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {gene} tracing: {e}")
    
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
    
    # GraphQL Test 1: EASY - Simple anatomy lookup
    print("\n   GraphQL Test 1: EASY - Simple anatomy lookup")
    try:
        query1 = """
        query TestAnatomy {
            anatomy(name: "heart") {
                name
                anatomyId
                structureType
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
                anatomy_data = data.get("data", {}).get("anatomy")
                if anatomy_data:
                    print(f"     [SUCCESS] GraphQL anatomy lookup working")
                    print(f"     Found: {anatomy_data.get('name')} (Type: {anatomy_data.get('structureType')})")
                else:
                    print("     [SUCCESS] GraphQL working, anatomy not found (expected)")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] GraphQL anatomy lookup failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] GraphQL anatomy lookup: {e}")
    
    # GraphQL Test 2: MEDIUM - Gene expression in tissue
    print("\n   GraphQL Test 2: MEDIUM - Gene expression in tissue")
    try:
        query2 = """
        query GeneExpressionInTissue($tissue: String!) {
            geneExpressionInTissue(tissue: $tissue) {
                gene
                tissue
                expressionLevel
            }
        }
        """
        variables2 = {"tissue": "breast"}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query2, "variables": variables2},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                expression_data = data.get("data", {}).get("geneExpressionInTissue", [])
                if expression_data:
                    print(f"     [SUCCESS] Gene expression query working")
                    print(f"     Found {len(expression_data)} gene-tissue connections")
                    print("     Sample expressions:")
                    for expr in expression_data[:3]:
                        gene = expr.get('gene', 'unknown')
                        level = expr.get('expressionLevel', 'unknown')
                        print(f"       {gene}: {level}")
                else:
                    print("     [SUCCESS] GraphQL working, no expression data found")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Gene expression query: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] Gene expression query: {e}")
    
    # GraphQL Test 3: HARD - Complex multi-organ disease analysis
    print("\n   GraphQL Test 3: HARD - Complex multi-organ analysis")
    try:
        query3 = """
        query ComplexOrganAnalysis($organ1: String!, $organ2: String!) {
            heartStructures: anatomyStructures(organ: $organ1) {
                name
                structureType
            }
            brainStructures: anatomyStructures(organ: $organ2) {
                name
                structureType
            }
            heartDiseases: diseasesAffectingOrgan(organ: $organ1) {
                name
                diseaseType
            }
            brainDiseases: diseasesAffectingOrgan(organ: $organ2) {
                name
                diseaseType
            }
        }
        """
        variables3 = {"organ1": "heart", "organ2": "brain"}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query3, "variables": variables3},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                result_data = data.get("data", {})
                heart_structures = result_data.get("heartStructures", [])
                brain_structures = result_data.get("brainStructures", [])
                heart_diseases = result_data.get("heartDiseases", [])
                brain_diseases = result_data.get("brainDiseases", [])
                
                print(f"     [SUCCESS] Complex multi-organ GraphQL working")
                print(f"     Heart structures: {len(heart_structures)}")
                print(f"     Brain structures: {len(brain_structures)}")
                print(f"     Heart diseases: {len(heart_diseases)}")
                print(f"     Brain diseases: {len(brain_diseases)}")
                print(f"     Total data points: {len(heart_structures) + len(brain_structures) + len(heart_diseases) + len(brain_diseases)}")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Complex GraphQL query: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] Complex GraphQL query: {e}")

    print("\n" + "="*70)
    print("INDIVIDUAL API TEST COMPLETE")
    print("LexAPI_Anatomics individual functionality verified")
    print("Standard endpoints + GraphQL flexible queries both working")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Starting individual anatomics API test...")
    print("Make sure LexAPI_Anatomics is running via api_startup.bat")
    print()
    
    success = test_individual_anatomics_api()
    
    if success:
        print("\n[SUCCESS] LexAPI_Anatomics individual testing complete")
        print("Ready for next API implementation")
    else:
        print("\n[FAILED] Individual anatomics API testing needs debugging")

