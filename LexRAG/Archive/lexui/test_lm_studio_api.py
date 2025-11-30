"""
Test LM Studio API
Test direct connection to LM Studio server with DNA Expert model
"""

import requests
import json

def test_lm_studio_api():
    """Test LM Studio server API"""
    
    print("TESTING LM STUDIO API")
    print("="*40)
    print("Server: http://192.168.50.236:1234")
    print("Model: dna-models (DNA Expert)")
    print("="*40)
    
    # Test 1: Check models endpoint
    print("\\n1. Testing models endpoint...")
    try:
        models_response = requests.get("http://192.168.50.236:1234/v1/models", timeout=10)
        if models_response.status_code == 200:
            models_data = models_response.json()
            print(f"   SUCCESS: {models_data}")
        else:
            print(f"   FAILED: HTTP {models_response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Simple chat
    print("\\n2. Testing simple chat...")
    try:
        chat_data = {
            "model": "dna-models",
            "messages": [
                {"role": "user", "content": "Hi, say hello back"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        chat_response = requests.post(
            "http://192.168.50.236:1234/v1/chat/completions",
            json=chat_data,
            timeout=30
        )
        
        print(f"   Status: HTTP {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_message = response_data['choices'][0]['message']['content']
                tokens = response_data.get('usage', {}).get('completion_tokens', 0)
                print(f"   SUCCESS: AI responded with {tokens} tokens")
                print(f"   Response: \"{ai_message}\"")
                return True
            else:
                print(f"   FAILED: Unexpected response format - {response_data}")
        else:
            print(f"   FAILED: HTTP {chat_response.status_code}")
            print(f"   Error: {chat_response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Genetics question
    print("\\n3. Testing genetics question...")
    try:
        genetics_data = {
            "model": "dna-models",
            "messages": [
                {"role": "user", "content": "What is BRCA1 in simple terms?"}
            ],
            "max_tokens": 150,
            "temperature": 0.5
        }
        
        genetics_response = requests.post(
            "http://192.168.50.236:1234/v1/chat/completions",
            json=genetics_data,
            timeout=30
        )
        
        if genetics_response.status_code == 200:
            response_data = genetics_response.json()
            ai_message = response_data['choices'][0]['message']['content']
            tokens = response_data.get('usage', {}).get('completion_tokens', 0)
            print(f"   SUCCESS: Genetics response with {tokens} tokens")
            print(f"   Response: \"{ai_message[:100]}...\"")
            return True
        else:
            print(f"   FAILED: HTTP {genetics_response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    return False

if __name__ == "__main__":
    print("Direct LM Studio API Test")
    print("Testing DNA Expert model responses")
    
    success = test_lm_studio_api()
    
    if success:
        print("\\nSUCCESS: LM Studio API is working!")
        print("Ready to fix frontend CORS issues")
    else:
        print("\\nFAILED: LM Studio API has issues")
        print("Check server status and model loading")
    
    input("\\nPress Enter to continue...")
