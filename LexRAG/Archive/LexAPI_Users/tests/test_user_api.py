"""
Test LexAPI_Users functionality
Basic API testing following LexRAG pattern
"""

import requests
import json
import time

def test_user_api():
    """Test LexAPI_Users endpoints"""
    base_url = "http://localhost:8007"
    
    print("Testing LexAPI_Users...")
    
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
    
    # Test user registration
    try:
        test_user = {
            "email": "test@example.com",
            "demographics": {
                "age": 35,
                "sex": "female", 
                "height_cm": 165,
                "weight_kg": 60,
                "ethnicity": "european"
            },
            "privacy_settings": {
                "data_sharing": False,
                "research_participation": True
            }
        }
        
        response = requests.post(f"{base_url}/users/register", json=test_user, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("user_id")
            print("✅ User registration passed")
            print(f"   User ID: {user_id}")
            
            # Test profile retrieval
            profile_response = requests.get(f"{base_url}/users/{user_id}/profile", timeout=10)
            if profile_response.status_code == 200:
                print("✅ Profile retrieval passed")
            else:
                print(f"❌ Profile retrieval failed: {profile_response.status_code}")
                
        else:
            print(f"❌ User registration failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ User registration error: {e}")

if __name__ == "__main__":
    test_user_api()
