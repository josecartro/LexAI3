"""
Diagnose New API Issues
Quick diagnostic for the 3 new APIs
"""

import requests
import time

def quick_test(api_name, port, endpoint="/health"):
    """Quick test of API endpoint"""
    try:
        print(f"Testing {api_name} (Port {port})...")
        response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
        
        if response.status_code == 200:
            print(f"  SUCCESS: {api_name} is responding")
            data = response.json()
            status = data.get("status", "unknown")
            print(f"  Status: {status}")
            return True
        else:
            print(f"  ERROR: {api_name} returned HTTP {response.status_code}")
            print(f"  Response: {response.text[:100]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ERROR: {api_name} not responding (not started or crashed)")
        return False
    except requests.exceptions.Timeout:
        print(f"  ERROR: {api_name} timed out (might be starting up)")
        return False
    except Exception as e:
        print(f"  ERROR: {api_name} - {e}")
        return False

def diagnose_new_apis():
    """Diagnose all 3 new APIs"""
    print("DIAGNOSING NEW APIS")
    print("="*40)
    
    # Test each new API
    results = {}
    
    # Test DNA Expert Model
    print("\\n1. DNA EXPERT MODEL SERVER")
    print("-" * 30)
    results["dna_model"] = quick_test("DNA Expert Model", 8010, "/health")
    
    # Test AIGateway
    print("\\n2. LEXAPI_AIGATEWAY")
    print("-" * 30)
    results["ai_gateway"] = quick_test("LexAPI_AIGateway", 8009)
    
    # Test DigitalTwin
    print("\\n3. LEXAPI_DIGITALTWIN")
    print("-" * 30)
    results["digital_twin"] = quick_test("LexAPI_DigitalTwin", 8008)
    
    # Summary
    print("\\n" + "="*40)
    print("DIAGNOSTIC SUMMARY")
    print("="*40)
    
    working = sum(results.values())
    total = len(results)
    
    print(f"Working APIs: {working}/{total}")
    
    for api, status in results.items():
        print(f"  {api}: {'WORKING' if status else 'FAILED'}")
    
    if working == total:
        print("\\nALL NEW APIS WORKING - Ready for AI integration!")
    else:
        print("\\nSome APIs need attention - check error messages above")
    
    return working == total

if __name__ == "__main__":
    diagnose_new_apis()
