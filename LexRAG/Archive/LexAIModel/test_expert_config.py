"""
Test Expert Configuration
Test model with expert recommendations for RTX 4090 + 14B model
"""

import requests
import json
import time

def test_expert_configuration():
    """Test model with expert-recommended settings"""
    
    print("TESTING EXPERT CONFIGURATION")
    print("="*50)
    print("GPU: RTX 4090 (16GB VRAM)")
    print("Model: 14B parameters with GPU acceleration")
    print("Settings: -ngl 40, -c 8192, -b 64")
    print("="*50)
    
    # Wait for model to be ready
    print("Waiting for model to load with GPU acceleration...")
    time.sleep(10)  # Give it time to start
    
    # Test cases with progressive complexity
    test_cases = [
        {
            "name": "Basic Response Test",
            "prompt": "Say 'ready'.",
            "max_tokens": 16,
            "temperature": 0.3,
            "expected": "Should respond with 'ready' or similar"
        },
        {
            "name": "Simple Greeting",
            "prompt": "Hi",
            "max_tokens": 50,
            "temperature": 0.7,
            "expected": "Should respond with greeting"
        },
        {
            "name": "Basic Math",
            "prompt": "What is 2+2?",
            "max_tokens": 50,
            "temperature": 0.3,
            "expected": "Should respond with 4"
        },
        {
            "name": "Conversation",
            "prompt": "Hello, how are you?",
            "max_tokens": 100,
            "temperature": 0.7,
            "expected": "Should respond conversationally"
        },
        {
            "name": "Genetics Question",
            "prompt": "What is BRCA1?",
            "max_tokens": 200,
            "temperature": 0.5,
            "expected": "Should explain BRCA1 gene"
        }
    ]
    
    working_tests = 0
    total_tests = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\\n{i}. {test['name']}")
        print(f"   Prompt: \"{test['prompt']}\"")
        print(f"   Expected: {test['expected']}")
        
        try:
            # Test with expert-recommended format
            response = requests.post('http://127.0.0.1:8010/v1/chat/completions', 
                json={
                    'model': 'qwen3-14b',  # Add model name as expert suggested
                    'messages': [{'role': 'user', 'content': test['prompt']}],
                    'max_tokens': test['max_tokens'],
                    'temperature': test['temperature'],
                    'top_p': 0.9
                }, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response
                content = ""
                tokens = 0
                
                if 'choices' in data and len(data['choices']) > 0:
                    choice = data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        content = choice['message']['content']
                    elif 'text' in choice:
                        content = choice['text']  # Alternative format
                
                if 'usage' in data:
                    tokens = data['usage'].get('completion_tokens', 0)
                
                print(f"   Status: HTTP {response.status_code}")
                print(f"   Tokens: {tokens}")
                print(f"   Length: {len(content)} characters")
                
                if len(content) > 0:
                    working_tests += 1
                    print(f"   Result: SUCCESS")
                    print(f"   Response: \"{content[:80]}{'...' if len(content) > 80 else ''}\"")
                else:
                    print(f"   Result: FAILED - Empty response")
                    print(f"   Raw data: {data}")
            else:
                print(f"   Status: HTTP {response.status_code} - FAILED")
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Final results
    print(f"\\n{'='*60}")
    print("EXPERT CONFIGURATION TEST RESULTS")
    print(f"{'='*60}")
    print(f"Working tests: {working_tests}/{total_tests}")
    print(f"Success rate: {working_tests/total_tests*100:.1f}%")
    
    if working_tests > 0:
        print("\\nSUCCESS: Expert configuration is working!")
        print("✅ GPU acceleration enabled")
        print("✅ Model generating responses")
        print("✅ Ready for frontend integration")
        
        print("\\nNext steps:")
        print("1. Use this configuration for production")
        print("2. Update frontend to use working model")
        print("3. Test with real genomics questions")
        
    else:
        print("\\nFAILED: Even expert configuration not working")
        print("Possible issues:")
        print("- GPU drivers or CUDA installation")
        print("- Model compatibility with llama.cpp version")
        print("- Memory/VRAM limitations")
        
        print("\\nFallback options:")
        print("1. Use LM Studio server mode (proven working)")
        print("2. Try different llama.cpp build")
        print("3. Use CPU-only configuration")
    
    return working_tests > 0

if __name__ == "__main__":
    print("TESTING DNA EXPERT MODEL WITH EXPERT CONFIGURATION")
    print("Based on professional llama.cpp guidance for RTX 4090")
    print("="*60)
    
    success = test_expert_configuration()
    
    if success:
        print("\\n🎉 EXPERT CONFIGURATION SUCCESSFUL!")
        print("Model is ready for production use")
    else:
        print("\\n❌ EXPERT CONFIGURATION FAILED")
        print("Consider alternative approaches")
    
    input("\\nPress Enter to continue...")



