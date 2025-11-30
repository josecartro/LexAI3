"""
Test Complete LexRAG System - All 5 APIs
Final system test to verify 100% LexRAG functionality
"""

import requests

def test_complete_lexrag_system():
    """Test all 5 LexRAG APIs"""
    print("="*80)
    print("TESTING COMPLETE LEXRAG SYSTEM - ALL 5 APIS")
    print("="*80)
    print("Final verification of the entire 7 Axes RAG system")
    
    apis = [
        ("LexAPI_Genomics", 8001, "Axes 2,3,4,6 (Genomics/Transcriptomics/Proteomics/Epigenomics)"),
        ("LexAPI_Anatomics", 8002, "Axis 1 (Anatomy/Structure)"),
        ("LexAPI_Literature", 8003, "Cross-Axis (Literature/Knowledge Search)"),
        ("LexAPI_Metabolics", 8005, "Axis 5 (Metabolomics/Biochemistry)"),
        ("LexAPI_Populomics", 8006, "Axis 7 (Exposome/Phenome/Population)")
    ]
    
    working_apis = 0
    total_apis = len(apis)
    
    print(f"\nTesting {total_apis} APIs across all 7 biological axes...")
    
    for api_name, port, description in apis:
        print(f"\n{'='*60}")
        print(f"TESTING: {api_name}")
        print(f"Purpose: {description}")
        print(f"Port: {port}")
        print('='*60)
        
        try:
            # Test health check
            r = requests.get(f"http://localhost:{port}/health", timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                service_name = data.get('service', 'unknown')
                print(f"[SUCCESS] {api_name} operational")
                print(f"  Service: {service_name}")
                
                # Test database connections
                databases = data.get('databases', {})
                if databases:
                    print("  Database connections:")
                    for db_name, db_info in databases.items():
                        status = db_info.get('status', 'unknown')
                        print(f"    {db_name}: {status}")
                
                # Test documentation
                docs = requests.get(f"http://localhost:{port}/docs", timeout=5)
                if docs.status_code == 200:
                    print("  Documentation: Available")
                
                # Test OpenAPI schema
                openapi = requests.get(f"http://localhost:{port}/openapi.json", timeout=5)
                if openapi.status_code == 200:
                    schema = openapi.json()
                    endpoints = list(schema.get('paths', {}).keys())
                    print(f"  Endpoints: {len(endpoints)} available")
                    if "/graphql" in endpoints:
                        print("  GraphQL: Available")
                
                working_apis += 1
                
            else:
                print(f"[ERROR] {api_name} failed: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"[OFFLINE] {api_name} not responding: {str(e)[:50]}")
    
    # Final system assessment
    print(f"\n{'='*80}")
    print("COMPLETE LEXRAG SYSTEM STATUS")
    print('='*80)
    print(f"Working APIs: {working_apis}/{total_apis}")
    
    success_rate = (working_apis / total_apis) * 100
    print(f"System Completion: {success_rate:.0f}%")
    
    if working_apis == total_apis:
        print("\n[PERFECT] 100% LEXRAG SYSTEM OPERATIONAL!")
        print("All 5 APIs working across all 7 biological axes")
        print("Ready for AI Model integration")
    elif working_apis >= 4:
        print(f"\n[EXCELLENT] {working_apis}/5 APIs operational")
        print("System ready for most AI Model use cases")
    elif working_apis >= 3:
        print(f"\n[GOOD] {working_apis}/5 APIs operational")
        print("Core system functional, need to complete remaining APIs")
    else:
        print(f"\n[NEEDS WORK] Only {working_apis}/5 APIs working")
        print("System needs more development")
    
    print(f"\n{'='*80}")
    print("LEXRAG 7 AXES COVERAGE:")
    print("- Axis 1 (Anatomy): LexAPI_Anatomics")
    print("- Axes 2,3,4,6 (Genomics/Transcriptomics/Proteomics/Epigenomics): LexAPI_Genomics") 
    print("- Axis 5 (Metabolomics): LexAPI_Metabolics")
    print("- Axis 7 (Exposome/Phenome): LexAPI_Populomics")
    print("- Cross-Axis (Literature): LexAPI_Literature")
    print('='*80)
    
    return working_apis, total_apis

if __name__ == "__main__":
    working, total = test_complete_lexrag_system()
    
    if working == total:
        print(f"\n🎉 COMPLETE SUCCESS: {working}/{total} APIs operational")
        print("🚀 LexRAG system ready for AI Model integration!")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {working}/{total} APIs operational")
        print("🔧 Continue development to complete system")

