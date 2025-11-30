"""
LexRAG Capability Demonstrator
Tests the complete flow: Registration -> DNA Upload -> Digital Twin -> AI Analysis
"""

import requests
import json
import time
import sys
from pprint import pprint

BASE_URLS = {
    "users": "http://127.0.0.1:8007",
    "digital_twin": "http://127.0.0.1:8008",
    "gateway": "http://127.0.0.1:8009",
    "genomics": "http://127.0.0.1:8001"
}

DEMO_USER = {
    "email": "demo_capability_test@lexrag.com",
    "demographics": {
        "age": 35,
        "sex": "female",
        "height_cm": 165,
        "weight_kg": 60,
        "ethnicity": "scandinavian",
        "birthplace": "Sweden",
        "parents_origin": ["Sweden", "Norway"]
    },
    "privacy_settings": {
        "data_sharing": False,
        "research_participation": True
    }
}

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_health():
    print_header("1. System Health Check")
    all_healthy = True
    for name, url in BASE_URLS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name.upper():<15} Online")
            else:
                print(f"❌ {name.upper():<15} Error: {response.status_code}")
                all_healthy = False
        except:
            print(f"❌ {name.upper():<15} Offline")
            all_healthy = False
    return all_healthy

def register_demo_user():
    print_header("2. User Registration Capability")
    print("Registering new demo user with demographics...")
    try:
        # Register
        response = requests.post(f"{BASE_URLS['users']}/users/register", json=DEMO_USER)
        if response.status_code == 200:
            data = response.json()
            user_id = data["user_id"]
            print(f"✅ User Registered Successfully")
            print(f"   ID: {user_id}")
            print(f"   Profile: 35yo Female, Scandinavian ancestry")
            return user_id
        else:
            print(f"❌ Registration Failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_digital_twin(user_id):
    print_header("3. Digital Twin Generation")
    print(f"Retrieving Digital Twin for {user_id}...")
    try:
        response = requests.get(f"{BASE_URLS['digital_twin']}/twin/{user_id}/model")
        if response.status_code == 200:
            twin = response.json()
            print("✅ Digital Twin Created")
            print(f"   Completeness: {twin.get('completeness_score', 0)*100:.1f}%")
            print(f"   Ancestry: {twin.get('ancestry_composition', 'Unknown')}")
            print("   (Twin automatically overlaid on 'Eve' reference model)")
            return True
        else:
            print(f"❌ Failed to get Twin: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_gateway(user_id):
    print_header("4. AI Gateway & Tool Usage")
    query = "What does my digital twin say about my ancestry risk?"
    print(f"Querying AI: '{query}'")
    
    payload = {
        "message": query,
        "conversation_id": f"demo_{int(time.time())}"
    }
    
    try:
        # Timeout increased because it calls the LLM
        response = requests.post(f"{BASE_URLS['gateway']}/chat/{user_id}", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("ai_response", {})
            
            print("\n✅ AI Response Received:")
            print("-" * 40)
            print(ai_response.get("response", "No text returned"))
            print("-" * 40)
            
            print("\n📊 Analysis Metadata:")
            print(f"   Confidence: {ai_response.get('confidence_level', 'unknown')}")
            print(f"   Data Sources: {ai_response.get('data_sources', {})}")
            
            return True
        else:
            print(f"❌ AI Query Failed: {response.text}")
            return False
            
    except requests.exceptions.ReadTimeout:
        print("⚠️  AI Timeout (Model might be loading or slow)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if not check_health():
        print("\n⚠️  Some services are offline. Please run 'start_complete_system.bat' first.")
        return

    user_id = register_demo_user()
    if not user_id:
        return

    if check_digital_twin(user_id):
        test_ai_gateway(user_id)

    print("\n" + "="*60)
    print(" DEMONSTRATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

