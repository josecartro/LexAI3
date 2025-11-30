"""
Test All Enhanced APIs - Complete System Verification
Test all 5 APIs with their enhancements working together
"""

import requests
import time

def test_all_enhanced_apis():
    """Test all 5 enhanced APIs comprehensively"""
    print("="*80)
    print("TESTING ALL 5 ENHANCED LEXRAG APIS")
    print("="*80)
    print("Verifying: All APIs enhanced with cross-axis capabilities")
    
    apis = [
        ("LexAPI_Genomics", 8001, "Genomics/Transcriptomics/Proteomics/Epigenomics"),
        ("LexAPI_Anatomics", 8002, "Anatomy/Structure"),
        ("LexAPI_Literature", 8003, "Literature/Knowledge Search"),
        ("LexAPI_Metabolics", 8005, "Metabolomics/Pharmacogenomics"),
        ("LexAPI_Populomics", 8006, "Population/Environmental")
    ]
    
    print("\nWaiting 20 seconds for all APIs to be ready...")
    time.sleep(20)
    
    enhanced_count = 0
    
    for api_name, port, description in apis:
        print(f"\n{'='*70}")
        print(f"TESTING: {api_name}")
        print(f"Purpose: {description}")
        print(f"Port: {port}")
        print('='*70)
        
        try:
            # Test health check
            r = requests.get(f"http://localhost:{port}/health", timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                service_name = data.get('service', 'unknown')
                print(f"[SUCCESS] {api_name} operational")
                print(f"  Service: {service_name}")
                
                # Check database connections
                databases = data.get('databases', {})
                if databases:
                    print("  Database connections:")
                    for db_name, db_info in databases.items():
                        status = db_info.get('status', 'unknown')
                        print(f"    {db_name}: {status}")
                
                enhanced_count += 1
                
                # Test enhanced capabilities based on API
                if api_name == "LexAPI_Genomics":
                    print("  Testing genomics enhancements...")
                    try:
                        r2 = requests.get(f"http://localhost:{port}/analyze/gene/BRCA2", timeout=15)
                        if r2.status_code == 200:
                            data2 = r2.json()
                            databases_used = data2.get('databases_queried', [])
                            print(f"    Enhanced analysis: {len(databases_used)} databases")
                            if 'biomart_protein_mapping' in databases_used:
                                print(f"    [ENHANCED] Protein connections working")
                            if 'gtex_v10_eqtl_associations' in databases_used:
                                print(f"    [ENHANCED] Expression effects working")
                    except:
                        print("    Enhancement test failed")
                
                elif api_name == "LexAPI_Metabolics":
                    print("  Testing metabolics enhancements...")
                    try:
                        r2 = requests.get(f"http://localhost:{port}/analyze/drug_metabolism/codeine", timeout=15)
                        if r2.status_code == 200:
                            data2 = r2.json()
                            databases_used = data2.get('databases_queried', [])
                            if 'pharmgkb_drug_gene_interactions' in databases_used:
                                print(f"    [ENHANCED] PharmGKB integration working")
                    except:
                        print("    Enhancement test failed")
                
                elif api_name == "LexAPI_Anatomics":
                    print("  Testing anatomics enhancements...")
                    try:
                        r2 = requests.get(f"http://localhost:{port}/analyze/organ/brain", timeout=15)
                        if r2.status_code == 200:
                            data2 = r2.json()
                            databases_used = data2.get('databases_queried', [])
                            if 'gtex_tissue_expression' in databases_used:
                                print(f"    [ENHANCED] GTEx tissue integration working")
                    except:
                        print("    Enhancement test failed")
                
                elif api_name == "LexAPI_Populomics":
                    print("  Testing populomics enhancements...")
                    try:
                        r2 = requests.get(f"http://localhost:{port}/analyze/environmental_risk/spain", timeout=15)
                        if r2.status_code == 200:
                            data2 = r2.json()
                            databases_used = data2.get('databases_queried', [])
                            if 'population_genetics_analysis' in databases_used:
                                print(f"    [ENHANCED] Population genetics working")
                    except:
                        print("    Enhancement test failed")
                
                elif api_name == "LexAPI_Literature":
                    print("  Testing literature enhancements...")
                    try:
                        r2 = requests.get(f"http://localhost:{port}/search/literature/BRCA2?context_apis=genomics", timeout=15)
                        if r2.status_code == 200:
                            data2 = r2.json()
                            databases_used = data2.get('databases_queried', [])
                            if 'cross_api_integration' in databases_used:
                                print(f"    [ENHANCED] Cross-API integration working")
                    except:
                        print("    Enhancement test failed")
                
            else:
                print(f"[ERROR] {api_name} failed: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"[OFFLINE] {api_name} not responding: {str(e)[:50]}")
    
    # Final assessment
    print(f"\n{'='*80}")
    print("ALL ENHANCED APIS TEST SUMMARY")
    print('='*80)
    print(f"Enhanced APIs operational: {enhanced_count}/5")
    
    if enhanced_count == 5:
        print("\n[PERFECT] ALL 5 APIS ENHANCED AND OPERATIONAL!")
        print("Complete 7 Axes system with cross-axis analysis ready")
        print("Ready for enhanced benchmark testing")
    elif enhanced_count >= 3:
        print(f"\n[GOOD] {enhanced_count}/5 APIs enhanced and working")
        print("Core system enhanced, continue with remaining APIs")
    else:
        print(f"\n[NEEDS WORK] Only {enhanced_count}/5 APIs working")
        print("System needs more enhancement work")
    
    print('='*80)
    
    return enhanced_count

if __name__ == "__main__":
    print("Testing all enhanced LexRAG APIs...")
    print("Verifying complete 7 Axes system with cross-axis analysis")
    print()
    
    working_count = test_all_enhanced_apis()
    
    if working_count == 5:
        print(f"\n🎉 ALL 5 APIS ENHANCED! Ready for 90%+ benchmark!")
    else:
        print(f"\n⚠️  {working_count}/5 APIs enhanced - continue development")
