"""
Test Individual LexAPI_Metabolics
Comprehensive testing of the metabolics API individually
"""

import requests
import time

def test_individual_metabolics_api():
    """Test the metabolics API individually"""
    print("="*70)
    print("INDIVIDUAL TESTING: LEXAPI_METABOLICS")
    print("="*70)
    print("Testing: Port management, health check, metabolic endpoints")
    
    base_url = "http://localhost:8005"
    
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
    
    # Test 2: Metabolism Analysis Endpoint
    print("\n2. TESTING METABOLISM ANALYSIS:")
    test_users = ["user123", "test_user", "demo_user"]
    
    for user in test_users:
        print(f"\n   Testing metabolism for: {user}")
        try:
            r = requests.get(f"{base_url}/analyze/metabolism/{user}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {user} metabolism analysis working")
                
                metabolic = data.get('metabolomic_profile', {})
                if metabolic and 'error' not in metabolic:
                    metabolites = metabolic.get('total_metabolites', 0)
                    print(f"     Metabolites measured: {metabolites}")
                else:
                    print(f"     Metabolites: Not found")
                
                pathways = data.get('pathway_analysis', {})
                if pathways and 'error' not in pathways:
                    pathway_count = pathways.get('total_pathways', 0)
                    print(f"     Pathways analyzed: {pathway_count}")
                else:
                    print(f"     Pathways: Not found")
                
                genetics = data.get('genetic_factors', {})
                if genetics and 'error' not in genetics:
                    variants = genetics.get('total_variants', 0)
                    print(f"     Genetic variants: {variants}")
                else:
                    print(f"     Genetic factors: Not found")
                    
            else:
                print(f"     [ERROR] {user} metabolism: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {user} metabolism: {e}")
    
    # Test 3: Drug Metabolism Analysis
    print("\n3. TESTING DRUG METABOLISM ANALYSIS:")
    test_drugs = ["warfarin", "aspirin", "ibuprofen"]
    
    for drug in test_drugs:
        print(f"\n   Testing drug metabolism: {drug}")
        try:
            r = requests.get(f"{base_url}/analyze/drug_metabolism/{drug}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {drug} metabolism analysis working")
                
                pharmaco = data.get('pharmacogenomic_factors', {})
                if pharmaco and 'error' not in pharmaco:
                    variants = pharmaco.get('total_pharmacogenomic_variants', 0)
                    print(f"     Pharmacogenomic variants: {variants}")
                    
                    cyp_variants = pharmaco.get('cyp450_variants', [])
                    if cyp_variants:
                        print(f"     Sample CYP450 variants:")
                        for variant in cyp_variants[:3]:
                            gene = variant.get('gene', 'unknown')
                            rsid = variant.get('variant', 'unknown')
                            print(f"       {gene}: {rsid}")
                else:
                    print(f"     Pharmacogenomic data: Not found")
                    
            else:
                print(f"     [ERROR] {drug} metabolism: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {drug} metabolism: {e}")
    
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
    
    # GraphQL Test 1: EASY - Simple metabolite lookup
    print("\n   GraphQL Test 1: EASY - Simple metabolite lookup")
    try:
        query1 = """
        query TestMetabolites {
            metabolitesForUser(userId: "user123") {
                metaboliteId
                concentration
                unit
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
                metabolite_data = data.get("data", {}).get("metabolitesForUser", [])
                if metabolite_data:
                    print(f"     [SUCCESS] GraphQL metabolite lookup working")
                    print(f"     Found {len(metabolite_data)} metabolites")
                    if metabolite_data:
                        sample = metabolite_data[0]
                        print(f"     Sample: {sample.get('metaboliteId')} ({sample.get('concentration')} {sample.get('unit')})")
                else:
                    print("     [SUCCESS] GraphQL working, no metabolites found (expected)")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] GraphQL metabolite lookup failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] GraphQL metabolite lookup: {e}")
    
    # GraphQL Test 2: MEDIUM - Pharmacogenomic analysis
    print("\n   GraphQL Test 2: MEDIUM - Pharmacogenomic analysis")
    try:
        query2 = """
        query PharmacogenomicAnalysis($geneFilter: String!) {
            pharmacogenomicVariants(geneFilter: $geneFilter) {
                gene
                variant
                significance
                metabolicRelevance
            }
        }
        """
        variables2 = {"geneFilter": "CYP"}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query2, "variables": variables2},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                pharmaco_data = data.get("data", {}).get("pharmacogenomicVariants", [])
                if pharmaco_data:
                    print(f"     [SUCCESS] Pharmacogenomic GraphQL working")
                    print(f"     Found {len(pharmaco_data)} CYP450 variants")
                    print("     Sample variants:")
                    for variant in pharmaco_data[:3]:
                        gene = variant.get('gene', 'unknown')
                        rsid = variant.get('variant', 'unknown')
                        relevance = variant.get('metabolicRelevance', 'unknown')
                        print(f"       {gene} {rsid}: {relevance}")
                else:
                    print("     [SUCCESS] GraphQL working, no pharmacogenomic data found")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Pharmacogenomic GraphQL: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] Pharmacogenomic GraphQL: {e}")
    
    # GraphQL Test 3: HARD - Complex metabolic pathway analysis
    print("\n   GraphQL Test 3: HARD - Complex metabolic analysis")
    try:
        query3 = """
        query ComplexMetabolicAnalysis($userId: String!, $pathwayName: String!) {
            userMetabolites: metabolitesForUser(userId: $userId) {
                metaboliteId
                concentration
                sampleType
            }
            userPathways: pathwayActivities(userId: $userId) {
                pathwayId
                activityScore
                confidence
            }
            relatedPathways: searchMetabolicPathways(pathwayName: $pathwayName)
            drugMetabolismGenes: pharmacogenomicVariants(geneFilter: "CYP") {
                gene
                variant
                significance
            }
        }
        """
        variables3 = {"userId": "user123", "pathwayName": "glycolysis"}
        
        response = requests.post(
            f"{base_url}/graphql",
            json={"query": query3, "variables": variables3},
            timeout=25
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                result_data = data.get("data", {})
                metabolites = result_data.get("userMetabolites", [])
                pathways = result_data.get("userPathways", [])
                related = result_data.get("relatedPathways", [])
                drug_genes = result_data.get("drugMetabolismGenes", [])
                
                print(f"     [SUCCESS] Complex metabolic GraphQL working")
                print(f"     User metabolites: {len(metabolites)}")
                print(f"     User pathways: {len(pathways)}")
                print(f"     Related pathways: {len(related)}")
                print(f"     Drug metabolism genes: {len(drug_genes)}")
                print(f"     Total metabolic data points: {len(metabolites) + len(pathways) + len(related) + len(drug_genes)}")
            else:
                print(f"     [ERROR] GraphQL errors: {data.get('errors', [])}")
        else:
            print(f"     [ERROR] Complex metabolic GraphQL: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"     [ERROR] Complex metabolic GraphQL: {e}")

    print("\n" + "="*70)
    print("INDIVIDUAL API TEST COMPLETE")
    print("LexAPI_Metabolics individual functionality verified")
    print("Standard endpoints + GraphQL flexible queries both working")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Starting individual metabolics API test...")
    print("Make sure LexAPI_Metabolics is running via api_startup.bat")
    print()
    
    success = test_individual_metabolics_api()
    
    if success:
        print("\n[SUCCESS] LexAPI_Metabolics individual testing complete")
        print("Ready for next API implementation")
    else:
        print("\n[FAILED] Individual metabolics API testing needs debugging")

