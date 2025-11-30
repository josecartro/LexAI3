"""
Test IPv4 Fix for Model Generation
Quick test to see if IPv4 binding fixes the generation issue
"""

import requests
import json
import time
import subprocess

def test_ipv4_model():
    """Test model with IPv4 binding"""
    
    print("TESTING DNA EXPERT MODEL WITH IPv4 FIX")
    print("="*50)
    print("Using 127.0.0.1 instead of 0.0.0.0 for host binding")
    print("="*50)
    
    # Kill any existing model process
    print("Stopping any existing model servers...")
    try:
        subprocess.run(['taskkill', '/F', '/PIM', 'python.exe'], 
                      capture_output=True, shell=True)
    except:
        pass
    
    time.sleep(3)
    
    # Start model with IPv4 binding
    print("\\nStarting model with IPv4 binding...")
    print("Command: python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 127.0.0.1 --port 8010 --n_ctx 2048")
    
    try:
        model_process = subprocess.Popen([
            'python', '-m', 'llama_cpp.server',
            '--model', 'qwen3-dna-expert.Q4_K_M.gguf',
            '--host', '127.0.0.1',
            '--port', '8010', 
            '--n_ctx', '2048'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("Model starting... waiting 60 seconds for full load...")
        time.sleep(60)
        
        # Test basic generation
        print("\\nTesting basic generation...")
        
        test_cases = [
            {"prompt": "Hi", "description": "Simple greeting"},
            {"prompt": "What is 2+2?", "description": "Basic math"},
            {"prompt": "Hello, how are you?", "description": "Conversation starter"}
        ]
        
        working_tests = 0
        
        for test in test_cases:
            print(f"\\nTesting: {test['description']}")
            print(f"Prompt: \"{test['prompt']}\"")
            
            try:
                response = requests.post('http://127.0.0.1:8010/v1/chat/completions', 
                    json={
                        'messages': [{'role': 'user', 'content': test['prompt']}],
                        'max_tokens': 100,
                        'temperature': 0.7
                    }, 
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'] if 'choices' in data else ''
                    tokens = data.get('usage', {}).get('completion_tokens', 0)
                    
                    print(f"  Status: HTTP {response.status_code}")
                    print(f"  Tokens: {tokens}")
                    print(f"  Content: \"{content[:100]}{'...' if len(content) > 100 else ''}\"")
                    
                    if len(content) > 0:
                        working_tests += 1
                        print("  Result: SUCCESS - Model is generating!")
                    else:
                        print("  Result: FAILED - Still empty")
                else:
                    print(f"  Status: HTTP {response.status_code} - FAILED")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Results
        print(f"\\n{'='*50}")
        print("IPv4 TEST RESULTS")
        print(f"{'='*50}")
        print(f"Working tests: {working_tests}/{len(test_cases)}")
        
        if working_tests > 0:
            print("SUCCESS: IPv4 fix resolved the generation issue!")
            print("The model can now generate responses properly")
            print("Frontend chat should work with IPv4 connection")
        else:
            print("FAILED: IPv4 fix did not resolve generation issue")
            print("The problem is deeper than network binding")
            print("May need LM Studio server mode or different approach")
        
        # Cleanup
        try:
            model_process.terminate()
        except:
            pass
        
        return working_tests > 0
        
    except Exception as e:
        print(f"Test setup failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing IPv4 fix for DNA Expert model generation")
    
    success = test_ipv4_model()
    
    if success:
        print("\\nRECOMMENDATION: Use IPv4 binding for model server")
        print("Update frontend to use 127.0.0.1:8010")
    else:
        print("\\nRECOMMENDATION: Consider LM Studio server mode")
        print("llama.cpp may have compatibility issues with this model")
    
    input("\\nPress Enter to continue...")



