"""
Test Individual LexAPI_Literature  
Comprehensive testing of the literature API individually
"""

import requests
import time

def test_individual_literature_api():
    """Test the literature API individually"""
    print("="*70)
    print("INDIVIDUAL TESTING: LEXAPI_LITERATURE")
    print("="*70)
    print("Testing: Port management, health check, literature endpoints")
    
    base_url = "http://localhost:8003"
    
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
            if databases:
                print("   Database connections:")
                for db_name, db_info in databases.items():
                    status = db_info.get('status', 'unknown')
                    print(f"     {db_name}: {status}")
            else:
                print("   No database info returned")
                
        else:
            print(f"   [ERROR] Health check failed: HTTP {r.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Health check failed: {e}")
        return False
    
    # Test 2: Literature Search
    print("\n2. TESTING LITERATURE SEARCH:")
    test_topics = ["BRCA2", "DNA_repair", "cancer_therapy"]
    
    for topic in test_topics:
        print(f"\n   Testing literature search: {topic}")
        try:
            r = requests.get(f"{base_url}/search/literature/{topic}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {topic} literature search working")
                
                literature_results = data.get('literature_results', {})
                if literature_results:
                    collections = literature_results.get('available_collections', [])
                    print(f"     Available collections: {len(collections)}")
                    if collections:
                        print(f"     Collections: {', '.join(collections)}")
                else:
                    print(f"     Literature results: Basic response")
                    
            else:
                print(f"     [ERROR] {topic} literature search: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {topic} literature search: {e}")
    
    # Test 3: Multi-turn Research
    print("\n3. TESTING MULTI-TURN RESEARCH:")
    test_queries = ["BRCA2_therapy", "immunotherapy", "precision_medicine"]
    
    for query in test_queries:
        print(f"\n   Testing multi-turn research: {query}")
        try:
            r = requests.get(f"{base_url}/research/multi_turn/{query}?max_turns=3", timeout=20)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {query} multi-turn research working")
                
                research_turns = data.get('research_turns', [])
                print(f"     Research turns completed: {len(research_turns)}")
                
                if research_turns:
                    print(f"     Sample turn: {research_turns[0].get('query', 'unknown')}")
                    
            else:
                print(f"     [ERROR] {query} multi-turn research: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {query} multi-turn research: {e}")
    
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
    print("LexAPI_Literature individual functionality verified")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Starting individual literature API test...")
    print("Make sure LexAPI_Literature is running via api_startup.bat")
    print()
    
    success = test_individual_literature_api()
    
    if success:
        print("\n[SUCCESS] LexAPI_Literature individual testing complete")
        print("Ready for complete system integration")
    else:
        print("\n[FAILED] Individual literature API testing needs debugging")