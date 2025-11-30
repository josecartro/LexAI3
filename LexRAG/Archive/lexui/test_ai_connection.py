"""
Test AI Model Connection
Test direct connection to DNA Expert model
"""

import requests
import json

def test_dna_expert_model():
    """Test direct connection to DNA Expert model"""
    
    print("TESTING DNA EXPERT MODEL CONNECTION")
    print("="*50)
    
    # Test 1: Check if model is available
    print("1. Testing model availability...")
    try:
        models_response = requests.get("http://127.0.0.1:8010/v1/models", timeout=10)
        if models_response.status_code == 200:
            models_data = models_response.json()
            print(f"   SUCCESS: Model available - {models_data}")
        else:
            print(f"   FAILED: HTTP {models_response.status_code}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test 2: Simple chat completion
    print("\\n2. Testing chat completion...")
    try:
        chat_data = {
            "messages": [
                {"role": "user", "content": "What is BRCA1?"}
            ],
            "max_tokens": 100,
            "temperature": 0.3
        }
        
        chat_response = requests.post(
            "http://127.0.0.1:8010/v1/chat/completions",
            json=chat_data,
            timeout=30
        )
        
        print(f"   Status: HTTP {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_message = response_data['choices'][0]['message']['content']
                print(f"   SUCCESS: AI responded")
                print(f"   Response: {ai_message[:100]}...")
                return True
            else:
                print(f"   FAILED: Unexpected response format - {response_data}")
                return False
        else:
            print(f"   FAILED: HTTP {chat_response.status_code}")
            print(f"   Error: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_ai_gateway():
    """Test AI Gateway as backup"""
    
    print("\\n3. Testing AI Gateway (backup)...")
    try:
        gateway_response = requests.get("http://127.0.0.1:8009/health", timeout=10)
        if gateway_response.status_code == 200:
            health_data = gateway_response.json()
            print(f"   Gateway status: {health_data.get('status')}")
            print(f"   AI model status: {health_data.get('ai_model', {}).get('status')}")
            return health_data.get('status') == 'healthy'
        else:
            print(f"   Gateway failed: HTTP {gateway_response.status_code}")
            return False
    except Exception as e:
        print(f"   Gateway error: {e}")
        return False

if __name__ == "__main__":
    print("AI CONNECTION DIAGNOSTIC")
    print("="*50)
    
    model_works = test_dna_expert_model()
    gateway_works = test_ai_gateway()
    
    print("\\n" + "="*50)
    print("CONNECTION TEST RESULTS")
    print("="*50)
    print(f"Direct model: {'WORKING' if model_works else 'FAILED'}")
    print(f"AI Gateway: {'WORKING' if gateway_works else 'FAILED'}")
    
    if model_works:
        print("\\nSUCCESS: DNA Expert model is working!")
        print("Frontend should be able to chat with AI directly")
    elif gateway_works:
        print("\\nPARTIAL: AI Gateway working, but model connection issues")
        print("Frontend can use gateway as fallback")
    else:
        print("\\nFAILED: Both AI systems have issues")
        print("Need to debug AI model and gateway connections")
    
    input("\\nPress Enter to continue...")



