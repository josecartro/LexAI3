"""
Test New APIs Simple
Check if the 3 new APIs are working
"""

import requests
import time

def test_new_apis():
    """Test the 3 new APIs"""
    print("Testing New APIs")
    print("="*30)
    
    # Wait a moment for startup
    print("Waiting 10 seconds for APIs to start...")
    time.sleep(10)
    
    # Test DNA Expert Model
    print("\\n1. DNA Expert Model (Port 8010)")
    try:
        # Try different endpoints
        endpoints = ["/health", "/v1/models", "/docs", "/"]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8010{endpoint}", timeout=5)
                print(f"  {endpoint}: HTTP {response.status_code}")
                if response.status_code == 200:
                    print(f"    SUCCESS: {len(response.text)} chars")
                    break
            except:
                print(f"  {endpoint}: No response")
        
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test DigitalTwin
    print("\\n2. DigitalTwin API (Port 8008)")
    try:
        response = requests.get("http://localhost:8008/health", timeout=10)
        print(f"  Health: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Status: {data.get('status')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test AIGateway
    print("\\n3. AIGateway API (Port 8009)")
    try:
        response = requests.get("http://localhost:8009/health", timeout=10)
        print(f"  Health: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Status: {data.get('status')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test simple AI chat if AIGateway works
    print("\\n4. AI Integration Test")
    try:
        response = requests.post(
            "http://localhost:8009/chat/test_user",
            json={"message": "Hello, can you help me understand genetics?"},
            timeout=30
        )
        print(f"  AI Chat: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("ai_response", {}).get("response", "")
            print(f"    AI Response: {len(ai_response)} chars")
            print(f"    Sample: {ai_response[:100]}...")
    except Exception as e:
        print(f"  AI Chat ERROR: {e}")

if __name__ == "__main__":
    test_new_apis()
