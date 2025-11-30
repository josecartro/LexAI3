"""
Test Model Generation Issues
Based on Qwen3-14B documentation from Hugging Face
"""

import requests
import json

def test_model_generation():
    """Test different approaches to get the model generating responses"""
    
    print("TESTING DNA EXPERT MODEL GENERATION")
    print("="*50)
    print("Based on: https://huggingface.co/lmstudio-community/Qwen3-14B-GGUF")
    
    # Test 1: With /no_think parameter (from documentation)
    print("\\n1. Testing with /no_think parameter...")
    try:
        response = requests.post('http://127.0.0.1:8010/v1/chat/completions', 
            json={
                'messages': [{'role': 'user', 'content': 'What is BRCA1? /no_think'}],
                'max_tokens': 200,
                'temperature': 0.7,
                'top_p': 0.9,
                'stream': False
            }, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'] if 'choices' in data else ''
            completion_tokens = data.get('usage', {}).get('completion_tokens', 0)
            
            print(f"   Status: HTTP {response.status_code}")
            print(f"   Completion tokens: {completion_tokens}")
            print(f"   Content length: {len(content)}")
            
            if len(content) > 0:
                print(f"   SUCCESS: {content[:100]}...")
                return True
            else:
                print("   FAILED: Still empty response")
        else:
            print(f"   FAILED: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Simple greeting
    print("\\n2. Testing simple greeting...")
    try:
        response = requests.post('http://127.0.0.1:8010/v1/chat/completions', 
            json={
                'messages': [{'role': 'user', 'content': 'Hi'}],
                'max_tokens': 50,
                'temperature': 0.8,
                'stream': False
            }, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'] if 'choices' in data else ''
            print(f"   Simple response: \\\"{content}\\\"")
            
            if len(content) > 0:
                return True
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Different parameters
    print("\\n3. Testing with different parameters...")
    try:
        response = requests.post('http://127.0.0.1:8010/v1/chat/completions', 
            json={
                'messages': [{'role': 'user', 'content': 'Explain genetics in one sentence.'}],
                'max_tokens': 100,
                'temperature': 1.0,
                'top_p': 0.95,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0,
                'stream': False
            }, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'] if 'choices' in data else ''
            print(f"   Different params: \\\"{content[:50]}...\\\"")
            
            if len(content) > 0:
                return True
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    return False

if __name__ == "__main__":
    success = test_model_generation()
    
    if success:
        print("\\n✅ SUCCESS: Model generation is working!")
        print("Frontend chat should now work with real AI responses")
    else:
        print("\\n❌ FAILED: Model still not generating responses")
        print("May need different model configuration or chat format")
    
    input("\\nPress Enter to continue...")



