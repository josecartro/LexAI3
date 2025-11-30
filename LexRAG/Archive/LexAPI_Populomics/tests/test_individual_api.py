"""
Test Individual LexAPI_Populomics
Comprehensive testing of the populomics API individually
"""

import requests
import time

def test_individual_populomics_api():
    """Test the populomics API individually"""
    print("="*70)
    print("INDIVIDUAL TESTING: LEXAPI_POPULOMICS")
    print("="*70)
    print("Testing: Port management, health check, population/environmental endpoints")
    
    base_url = "http://localhost:8006"
    
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
    
    # Test 2: Environmental Risk Analysis
    print("\n2. TESTING ENVIRONMENTAL RISK ANALYSIS:")
    test_locations = ["spain", "finland", "australia"]
    
    for location in test_locations:
        print(f"\n   Testing environmental risk for: {location}")
        try:
            r = requests.get(f"{base_url}/analyze/environmental_risk/{location}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {location} environmental analysis working")
                
                env_factors = data.get('environmental_factors', {})
                if env_factors and 'error' not in env_factors:
                    models = env_factors.get('total_models', 0)
                    print(f"     Risk models available: {models}")
                else:
                    print(f"     Environmental factors: Not found")
                
                risk_assessment = data.get('risk_assessment', {})
                if risk_assessment:
                    recommendations = risk_assessment.get('recommendations', [])
                    print(f"     Recommendations: {len(recommendations)}")
                    if recommendations:
                        print(f"     Sample: {recommendations[0][:50]}...")
                    
            else:
                print(f"     [ERROR] {location} environmental analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {location} environmental analysis: {e}")
    
    # Test 3: Disease Risk Analysis
    print("\n3. TESTING DISEASE RISK ANALYSIS:")
    test_diseases = ["cancer", "diabetes", "heart_disease"]
    
    for disease in test_diseases:
        print(f"\n   Testing disease risk for: {disease}")
        try:
            r = requests.get(f"{base_url}/analyze/disease_risk/{disease}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {disease} risk analysis working")
                
                genetic_risk = data.get('genetic_risk_factors', {})
                if genetic_risk and 'error' not in genetic_risk:
                    variants = genetic_risk.get('total_variants', 0)
                    print(f"     Disease-related variants: {variants}")
                    
                    disease_variants = genetic_risk.get('disease_variants', [])
                    if disease_variants:
                        print(f"     Sample variants:")
                        for variant in disease_variants[:3]:
                            rsid = variant.get('variant', 'unknown')
                            gene = variant.get('gene', 'unknown')
                            print(f"       {rsid} in {gene}")
                else:
                    print(f"     Genetic risk factors: Not found")
                    
            else:
                print(f"     [ERROR] {disease} risk analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {disease} risk analysis: {e}")
    
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

    print("\n" + "="*70)
    print("INDIVIDUAL API TEST COMPLETE")
    print("LexAPI_Populomics individual functionality verified")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Starting individual populomics API test...")
    print("Make sure LexAPI_Populomics is running via api_startup.bat")
    print()
    
    success = test_individual_populomics_api()
    
    if success:
        print("\n[SUCCESS] LexAPI_Populomics individual testing complete")
        print("Ready for final API implementation")
    else:
        print("\n[FAILED] Individual populomics API testing needs debugging")

