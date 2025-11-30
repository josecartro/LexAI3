"""
Test LexAPI_DigitalTwin functionality
Basic API testing following LexRAG pattern
"""

import requests
import json
import time

def test_digital_twin_api():
    """Test LexAPI_DigitalTwin endpoints"""
    base_url = "http://localhost:8008"
    
    print("Testing LexAPI_DigitalTwin...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Databases: {health_data.get('databases', {}).keys()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test Adam reference model
    try:
        response = requests.get(f"{base_url}/twin/reference/adam", timeout=10)
        if response.status_code == 200:
            adam_data = response.json()
            print("✅ Adam reference model retrieval passed")
            print(f"   Model: {adam_data.get('model_name')}")
            print(f"   Age: {adam_data.get('demographics', {}).get('age_years')}")
        else:
            print(f"❌ Adam model retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Adam model error: {e}")
    
    # Test Eve reference model
    try:
        response = requests.get(f"{base_url}/twin/reference/eve", timeout=10)
        if response.status_code == 200:
            eve_data = response.json()
            print("✅ Eve reference model retrieval passed")
            print(f"   Model: {eve_data.get('model_name')}")
            print(f"   Age: {eve_data.get('demographics', {}).get('age_years')}")
        else:
            print(f"❌ Eve model retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Eve model error: {e}")
    
    # Test user digital twin (would need existing user)
    try:
        test_user_id = "test_user_123"
        response = requests.get(f"{base_url}/twin/{test_user_id}/model", timeout=15)
        if response.status_code == 200:
            twin_data = response.json()
            print("✅ User digital twin creation/retrieval passed")
            print(f"   Completeness: {twin_data.get('completeness_score', 0)*100:.1f}%")
        else:
            print(f"⚠️ User twin test: {response.status_code} (expected if no user exists)")
    except Exception as e:
        print(f"⚠️ User twin test error: {e} (expected if no user exists)")

if __name__ == "__main__":
    test_digital_twin_api()
