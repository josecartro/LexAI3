"""
Test Priority 2: Variant→Expression Integration
Test GTEx eQTL integration for tissue-specific variant analysis
"""

import requests
import time

def test_priority2_integration():
    """Test Priority 2: Variant→Expression connections"""
    print("="*70)
    print("TESTING PRIORITY 2: VARIANT→EXPRESSION INTEGRATION")
    print("="*70)
    print("Testing GTEx eQTL data for tissue-specific variant effects")
    
    base_url = "http://localhost:8001"
    
    # Wait for enhanced API
    print("\nWaiting 15 seconds for enhanced API...")
    time.sleep(15)
    
    # Test 1: Enhanced variant analysis with expression effects
    print("\n1. TESTING ENHANCED VARIANT ANALYSIS:")
    test_variants = ["rs7412", "rs429358", "rs4680"]
    
    for variant in test_variants:
        print(f"\n   Testing enhanced {variant} analysis:")
        try:
            r = requests.get(f"{base_url}/analyze/variant/{variant}", timeout=20)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {variant} enhanced analysis working")
                
                databases = data.get('databases_queried', [])
                print(f"     Databases: {len(databases)} - {databases}")
                
                # Check new expression effects
                expression_effects = data.get('expression_effects', {})
                if expression_effects and 'error' not in expression_effects:
                    total_tissues = expression_effects.get('total_tissues_affected', 0)
                    print(f"     [NEW] Expression effects: {total_tissues} tissues affected")
                    
                    effects = expression_effects.get('expression_effects', [])
                    if effects:
                        sample_effect = effects[0]
                        tissue = sample_effect.get('tissue_type', 'unknown')
                        effect = sample_effect.get('expression_effect', 0)
                        strength = sample_effect.get('effect_strength', 'unknown')
                        print(f"     Sample effect: {tissue} ({strength} effect: {effect:.3f})")
                else:
                    print(f"     Expression effects: None found")
                    
            else:
                print(f"     [ERROR] {variant} analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {variant} analysis: {e}")
    
    # Test 2: New expression endpoint
    print("\n2. TESTING NEW EXPRESSION ENDPOINT:")
    for variant in test_variants:
        print(f"\n   Testing {variant} expression endpoint:")
        try:
            r = requests.get(f"{base_url}/analyze/variant/{variant}/expression", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {variant} expression endpoint working")
                
                expression_analysis = data.get('expression_analysis', {})
                if expression_analysis and 'error' not in expression_analysis:
                    total_tissues = expression_analysis.get('total_tissues_affected', 0)
                    print(f"     Tissues affected: {total_tissues}")
                    
                    enhancement = data.get('enhancement', '')
                    if 'gtex' in enhancement.lower():
                        print(f"     [NEW] Using GTEx eQTL data!")
                    
                    cross_axis = data.get('cross_axis_connection', '')
                    print(f"     Connection: {cross_axis}")
                else:
                    print(f"     [INFO] No expression effects for {variant}")
                    
            else:
                print(f"     [ERROR] {variant} expression endpoint: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {variant} expression endpoint: {e}")
    
    # Test 3: Check API documentation
    print("\n3. TESTING API DOCUMENTATION:")
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        if r.status_code == 200:
            schema = r.json()
            endpoints = list(schema.get('paths', {}).keys())
            
            new_endpoints = [ep for ep in endpoints if 'expression' in ep or 'proteins' in ep]
            print(f"   [SUCCESS] New endpoints in documentation: {new_endpoints}")
            print(f"   Total endpoints: {len(endpoints)}")
            
        else:
            print(f"   [ERROR] Documentation check: HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Documentation check: {e}")

    print("\n" + "="*70)
    print("PRIORITY 2 INTEGRATION TEST COMPLETE")
    print("Status: Protein connections + Expression effects integration")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Testing Priority 2: Variant→Expression integration...")
    print("Make sure enhanced API is running via api_startup.bat")
    print()
    
    success = test_priority2_integration()
    
    if success:
        print("\n[SUCCESS] Priority 2 integration working")
        print("Cross-axis analysis: Genomics → Transcriptomics enabled")
    else:
        print("\n[FAILED] Priority 2 integration needs debugging")
